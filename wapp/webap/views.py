import base64
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, get_user_model
from django.core.cache import cache
from django.db.models import Q, F, Count
from rest_framework import permissions, viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from silk.profiling.profiler import silk_profile
import os
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from knox.models import AuthToken

from .models import BlogPost, PostComment, Category, Tag, UserInteraction, UserProfile
from .serializers import (
    BlogPostSerializer, PostCommentSerializer, UserSerializer, 
    CategorySerializer, TagSerializer, UserInteractionSerializer, UserProfileSerializer
)
from .forms import BlogPostCreateForm, BlogPostCommentForm
from .permissions import IsOwnerOrReadOnly

User = get_user_model()

# JWT-аутентифікація автоматично забезпечує отримання access/refresh токенів за допомогою rest_framework_simplejwt.
# Для цього додайте відповідні URL-ендпоінти у свій urls.py:
#   path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#   path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        token = AuthToken.objects.create(user)[1]
        return Response({"token": token})

# ViewSets для основних моделей
class CategoryViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class TagViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Отримати популярні теги"""
        popular_tags = Tag.objects.annotate(
            posts_count=Count('blogpost')
        ).order_by('-posts_count')[:20]
        
        serializer = self.get_serializer(popular_tags, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class BlogPostViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    serializer_class = BlogPostSerializer
    permission_classes = [IsOwnerOrReadOnly]  # Лише автор може редагувати/видаляти

    def get_queryset(self):
        posts = cache.get('all_posts')
        if not posts:
            posts = BlogPost.objects.all().select_related('author', 'category').prefetch_related('tags', 'postcomment_set')
            cache.set('all_posts', posts, timeout=300)  # Кешуємо на 5 хвилин
        return posts

    @silk_profile(name="blog_post_list")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Збільшуємо лічильник переглядів при отриманні поста"""
        instance = self.get_object()
        
        # Збільшуємо кількість переглядів
        BlogPost.objects.filter(id=instance.id).update(views_count=F('views_count') + 1)
        
        # Записуємо взаємодію користувача
        if request.user.is_authenticated:
            UserInteraction.objects.get_or_create(
                user=request.user,
                post=instance,
                interaction_type='view'
            )
        
        # Оновлюємо instance для відображення нової кількості переглядів
        instance.refresh_from_db()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Лайкнути/анлайкнути пост"""
        post = self.get_object()
        interaction, created = UserInteraction.objects.get_or_create(
            user=request.user,
            post=post,
            interaction_type='like'
        )
        
        if not created:
            # Якщо вже лайкнув, то видаляємо лайк
            interaction.delete()
            BlogPost.objects.filter(id=post.id).update(likes_count=F('likes_count') - 1)
            liked = False
        else:
            BlogPost.objects.filter(id=post.id).update(likes_count=F('likes_count') + 1)
            liked = True
        
        post.refresh_from_db()
        return Response({
            'liked': liked,
            'likes_count': post.likes_count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def save(self, request, pk=None):
        """Зберегти/видалити пост зі збережених"""
        post = self.get_object()
        interaction, created = UserInteraction.objects.get_or_create(
            user=request.user,
            post=post,
            interaction_type='save'
        )
        
        if not created:
            interaction.delete()
            saved = False
        else:
            saved = True
        
        return Response({'saved': saved})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Пошук постів"""
        query = request.GET.get('q', '')
        category_slug = request.GET.get('category', '')
        tag_slugs = request.GET.get('tags', '').split(',') if request.GET.get('tags') else []
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            )
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        if tag_slugs and tag_slugs[0]:
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()
        
        # Сортування
        sort_by = request.GET.get('sort', 'created_at')
        if sort_by == 'popular':
            queryset = queryset.order_by('-views_count', '-likes_count')
        elif sort_by == 'likes':
            queryset = queryset.order_by('-likes_count')
        elif sort_by == 'views':
            queryset = queryset.order_by('-views_count')
        else:
            queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def saved(self, request):
        """Отримати збережені пости користувача"""
        saved_posts = BlogPost.objects.filter(
            userinteraction__user=request.user,
            userinteraction__interaction_type='save'
        ).distinct()
        
        page = self.paginate_queryset(saved_posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(saved_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Популярні пости"""
        popular_posts = self.get_queryset().order_by('-views_count', '-likes_count')[:10]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для управління коментарями"""
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = PostComment.objects.all()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.select_related('author', 'post')
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class UserInteractionViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = UserInteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserInteraction.objects.filter(user=self.request.user)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для управління профілями користувачів"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# API для аналітики
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_analytics(request):
    """Аналітика для користувача"""
    user = request.user
    user_posts = BlogPost.objects.filter(author=user)
    
    analytics = {
        'total_posts': user_posts.count(),
        'total_views': sum(post.views_count for post in user_posts),
        'total_likes': sum(post.likes_count for post in user_posts),
        'total_comments': PostComment.objects.filter(post__author=user).count(),
        'top_posts': BlogPostSerializer(
            user_posts.order_by('-views_count')[:5], 
            many=True,
            context={'request': request}
        ).data,
        'popular_categories': list(
            Category.objects.filter(blogpost__author=user)
            .annotate(posts_count=Count('blogpost'))
            .order_by('-posts_count')
            .values('name', 'posts_count')[:5]
        )
    }
    
    return Response(analytics)

class SearchView(APIView):
    """API для пошуку блог-постів"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'results': []})
        
        posts = BlogPost.objects.filter(
            Q(title__icontains=query) | 
            Q(text__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:20]
        
        serializer = BlogPostSerializer(posts, many=True)
        return Response({'results': serializer.data})

class AnalyticsView(APIView):
    """API для отримання аналітики"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Загальна статистика
        total_posts = BlogPost.objects.count()
        total_users = User.objects.count()
        total_interactions = UserInteraction.objects.count()
        
        # Популярні пости
        popular_posts = BlogPost.objects.order_by('-views_count')[:5]
        popular_serializer = BlogPostSerializer(popular_posts, many=True)
        
        # Користувацька аналітика
        user_posts = BlogPost.objects.filter(author=request.user).count()
        user_interactions = UserInteraction.objects.filter(user=request.user).count()
        
        return Response({
            'global_stats': {
                'total_posts': total_posts,
                'total_users': total_users,
                'total_interactions': total_interactions,
            },
            'popular_posts': popular_serializer.data,
            'user_stats': {
                'posts_count': user_posts,
                'interactions_count': user_interactions,
            }
        })

# Веб-сторінкові функції (традиційний Django)
def index_view(request):
    if request.user.is_anonymous:  # Автоматична авторизація адміністратора за потреби
        user = authenticate(request, username=os.environ.get('BLOG_USER', 'admin'), password=os.environ.get('BLOG_PASS', 'admin123'))
        if user:
            login(request, user)

    all_posts = BlogPost.objects.select_related('author', 'category').prefetch_related('tags').all()
    categories = Category.objects.all()
    
    for b_post in all_posts:
        b_post.base64_image = base64.b64encode(b_post.post_picture).decode('utf-8') if b_post.post_picture else None

    return render(request, 'blog.html', {
        'blog_posts': all_posts,
        'categories': categories
    })

def create_post(request):
    if request.method == 'POST':
        form = BlogPostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            b_post = BlogPost(
                title=request.POST['title'],
                text=request.POST['text'],
                author=request.user,
                post_picture=request.FILES['post_picture'].read() if 'post_picture' in request.FILES else None
            )
            b_post.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = BlogPostCreateForm()
    return render(request, 'create_post.html', {'form': form, 'title': 'Створення нового допису'})

def display_post(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    
    # Збільшуємо кількість переглядів
    BlogPost.objects.filter(id=post_id).update(views_count=F('views_count') + 1)
    post.refresh_from_db()
    
    post.base64_image = base64.b64encode(post.post_picture).decode('utf-8') if post.post_picture else None
    comments = PostComment.objects.filter(post=post).select_related('author')
    form = BlogPostCommentForm()
    
    return render(request, "read_post.html", {
        "post": post, 
        "comments": comments, 
        "form": form
    })

def comment_post(request, post_id):
    post = get_object_or_404(BlogPost, pk=post_id)
    
    if request.method == 'POST':
        form = BlogPostCommentForm(request.POST)
        if form.is_valid():
            comment = PostComment(
                author=request.user,
                post=post,
                text=request.POST['text']
            )
            comment.save()
            return HttpResponseRedirect(reverse('display_post', args=[post_id]))
    
    post.base64_image = base64.b64encode(post.post_picture).decode('utf-8') if post.post_picture else None
    comments = PostComment.objects.filter(post=post).select_related('author')
    form = BlogPostCommentForm()
    
    return render(request, "read_post.html", {
        "post": post, 
        "comments": comments, 
        "form": form
    })
