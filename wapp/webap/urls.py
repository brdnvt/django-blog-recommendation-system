from django.urls import include, path
from rest_framework import routers
from knox import views as knox_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views
from knox.views import LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = routers.DefaultRouter()
router.register('authors', views.UserViewSet, basename='authors')
router.register('posts', views.BlogPostViewSet, basename='posts')
router.register('comments', views.CommentViewSet, basename='comments')
router.register(r'users', views.UserViewSet)
router.register('categories', views.CategoryViewSet, basename='categories')
router.register('tags', views.TagViewSet, basename='tags')
router.register('interactions', views.UserInteractionViewSet, basename='interactions')
router.register('profiles', views.UserProfileViewSet, basename='profiles')
urlpatterns = [
    path("", views.index_view, name="index"),
    path("create", views.create_post, name="create"),
    path("post/<int:post_id>/", views.display_post, name="display_post"),
    path('post/<int:post_id>/comment/', views.comment_post, name='comment_post'),
    path("api/", include(router.urls), name="api"),
    path('api/search/', views.SearchView.as_view(), name='search'),
    path('api/analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('api/login/', views.LoginView.as_view(), name='knox_login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('silk/', include('silk.urls', namespace='silk')),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
