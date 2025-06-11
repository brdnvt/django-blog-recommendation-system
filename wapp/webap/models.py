from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import re

User = get_user_model()

class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=100, unique=True)
    description = models.TextField('Опис категорії', blank=True)
    slug = models.SlugField('URL слаг', max_length=100, unique=True)
    color = models.CharField('Колір категорії', max_length=7, default='#007bff')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField('Назва тегу', max_length=50, unique=True)
    slug = models.SlugField('URL слаг', max_length=50, unique=True)
    color = models.CharField('Колір тегу', max_length=7, default='#6c757d')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField('Заголовок допису', max_length=56)
    text = models.TextField('Текст допису')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категорія')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Зображення зберігається як binary (можна замінити на ImageField за необхідності)
    post_picture = models.BinaryField('Зображення допису', null=True, blank=True)
    
    # Аналітика
    views_count = models.PositiveIntegerField('Кількість переглядів', default=0)
    likes_count = models.PositiveIntegerField('Кількість лайків', default=0)
    reading_time = models.PositiveIntegerField('Час читання (хв)', default=0)
    
    class Meta:
        verbose_name = 'Блог пост'
        verbose_name_plural = 'Блог пости'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Автоматичний розрахунок часу читання (200 слів за хвилину)
        if self.text:
            word_count = len(self.text.split())
            self.reading_time = max(1, word_count // 200)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('display_post', kwargs={'post_id': self.pk})
    
    def __str__(self):
        return self.title

class UserInteraction(models.Model):
    INTERACTION_TYPES = [
        ('like', 'Лайк'),
        ('dislike', 'Дизлайк'),
        ('save', 'Збереження'),
        ('share', 'Поділитись'),
        ('view', 'Перегляд'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    interaction_type = models.CharField('Тип взаємодії', max_length=10, choices=INTERACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Взаємодія користувача'
        verbose_name_plural = 'Взаємодії користувачів'
        unique_together = ['user', 'post', 'interaction_type']
    
    def __str__(self):
        return f'{self.user.username} - {self.get_interaction_type_display()} - {self.post.title}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField('Біографія', max_length=500, blank=True)
    avatar = models.BinaryField('Аватар', null=True, blank=True)
    interests = models.ManyToManyField(Tag, blank=True, verbose_name='Інтереси')
    follows = models.ManyToManyField(User, related_name='followers', blank=True, verbose_name='Підписки')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Профіль користувача'
        verbose_name_plural = 'Профілі користувачів'
    
    def __str__(self):
        return f'Профіль {self.user.username}'

class PostComment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    text = models.TextField(max_length=1024)
    last_modified = models.DateTimeField(auto_now_add=True)
    likes_count = models.PositiveIntegerField('Кількість лайків', default=0)
    
    class Meta:
        verbose_name = 'Коментар'
        verbose_name_plural = 'Коментарі'
        ordering = ['-last_modified']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'
