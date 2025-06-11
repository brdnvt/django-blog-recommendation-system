import base64
from rest_framework import serializers
from .models import BlogPost, PostComment, User, Category, Tag, UserInteraction, UserProfile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'color', 'created_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'color', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    interests = TagSerializer(many=True, read_only=True)
    avatar_base64 = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar_base64', 'interests', 'followers_count', 'following_count', 'created_at']
    
    def get_avatar_base64(self, obj):
        if obj.avatar:
            return base64.b64encode(obj.avatar).decode('utf-8')
        return None
    
    def get_followers_count(self, obj):
        return obj.user.followers.count()
    
    def get_following_count(self, obj):
        return obj.follows.count()

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data.get('email'),
            validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name')
        )
        # Створюємо профіль користувача
        UserProfile.objects.create(user=user)
        return user

class UserInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInteraction
        fields = ['id', 'user', 'post', 'interaction_type', 'timestamp']
        extra_kwargs = {'user': {'read_only': True}}

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Видаляємо попередню взаємодію того ж типу, якщо є
        UserInteraction.objects.filter(
            user=validated_data['user'],
            post=validated_data['post'],
            interaction_type=validated_data['interaction_type']
        ).delete()
        return super().create(validated_data)

class PostCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = PostComment
        fields = ['id', 'author', 'post', 'text', 'last_modified', 'likes_count', 'is_liked']
        extra_kwargs = {'author': {'read_only': True}}
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserInteraction.objects.filter(
                user=request.user,
                post_id=obj.post.id,
                interaction_type='like'
            ).exists()
        return False

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class BlogPostSerializer(serializers.ModelSerializer):
    # Включаємо коментарі; використовуємо поле 'postcomment_set' за замовчуванням
    comments = PostCommentSerializer(required=False, many=True, source="postcomment_set", read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    
    # Додаємо поле для отримання зображення у форматі base64
    base64_image = serializers.SerializerMethodField()
    
    # Взаємодії користувача з постом
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    
    # Ідентифікатори для створення/редагування
    category_id = serializers.IntegerField(write_only=True, required=False)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'author', 'title', 'text', 'category', 'category_id', 'tags', 'tag_ids',
            'comments', 'last_modified', 'created_at', 'base64_image', 'views_count', 
            'likes_count', 'reading_time', 'is_liked', 'is_saved'
        ]
        extra_kwargs = {'author': {'read_only': True}}

    def get_base64_image(self, obj):
        if obj.post_picture:
            return base64.b64encode(obj.post_picture).decode('utf-8')
        return None
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserInteraction.objects.filter(
                user=request.user,
                post=obj,
                interaction_type='like'
            ).exists()
        return False
    
    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserInteraction.objects.filter(
                user=request.user,
                post=obj,
                interaction_type='save'
            ).exists()
        return False

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        category_id = validated_data.pop('category_id', None)
        
        validated_data['author'] = self.context['request'].user
        
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        blog_post = super().create(validated_data)
        
        # Додаємо теги
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            blog_post.tags.set(tags)
        
        return blog_post
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        category_id = validated_data.pop('category_id', None)
        
        if category_id:
            try:
                validated_data['category'] = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass
        
        instance = super().update(instance, validated_data)
        
        # Оновлюємо теги
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        
        return instance
