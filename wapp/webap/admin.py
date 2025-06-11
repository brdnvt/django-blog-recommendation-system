from django.contrib import admin
from .models import BlogPost, PostComment, Category, Tag, UserInteraction, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'views_count', 'likes_count', 'reading_time', 'created_at']
    list_filter = ['category', 'tags', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'likes_count', 'reading_time', 'created_at']
    ordering = ['-created_at']

@admin.register(PostComment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'author', 'post', 'last_modified']
    list_filter = ['last_modified', 'author']
    search_fields = ['text', 'author__username', 'post__title']
    ordering = ['-last_modified']
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Comment Preview'

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'interaction_type', 'timestamp']
    list_filter = ['interaction_type', 'timestamp']
    search_fields = ['user__username', 'post__title']
    ordering = ['-timestamp']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio_preview', 'interest_count', 'follows_count']
    search_fields = ['user__username', 'bio']
    filter_horizontal = ['interests', 'follows']
    
    def bio_preview(self, obj):
        return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
    bio_preview.short_description = 'Bio Preview'
    
    def interest_count(self, obj):
        return obj.interests.count()
    interest_count.short_description = 'Interests'
    
    def follows_count(self, obj):
        return obj.follows.count()
    follows_count.short_description = 'Following'
