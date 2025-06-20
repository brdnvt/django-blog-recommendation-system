# Generated by Django 4.2.7 on 2025-06-11 16:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("webap", "0002_alter_blogpost_last_modified_and_more"),
    ]

    operations = [
        # Створення нових моделей
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Назва категорії')),
                ('description', models.TextField(blank=True, verbose_name='Опис категорії')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='URL слаг')),
                ('color', models.CharField(default='#007bff', max_length=7, verbose_name='Колір категорії')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Категорія',
                'verbose_name_plural': 'Категорії',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='Назва тегу')),
                ('slug', models.SlugField(max_length=50, unique=True, verbose_name='URL слаг')),
                ('color', models.CharField(default='#6c757d', max_length=7, verbose_name='Колір тегу')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
                'ordering': ['name'],
            },
        ),
        # Додання нових полів до BlogPost
        migrations.AddField(
            model_name='blogpost',
            name='views_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість переглядів'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='likes_count',
            field=models.PositiveIntegerField(default=0, verbose_name='Кількість лайків'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='reading_time',
            field=models.PositiveIntegerField(default=0, verbose_name='Час читання (хв)'),
        ),        migrations.AddField(
            model_name='blogpost',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogpost',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webap.category', verbose_name='Категорія'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=models.ManyToManyField(blank=True, to='webap.tag', verbose_name='Теги'),
        ),
        # Створення UserInteraction
        migrations.CreateModel(
            name='UserInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('like', 'Лайк'), ('dislike', 'Дизлайк'), ('save', 'Збереження'), ('share', 'Поділитись'), ('view', 'Перегляд')], max_length=10, verbose_name='Тип взаємодії')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webap.blogpost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Взаємодія користувача',
                'verbose_name_plural': 'Взаємодії користувачів',
            },
        ),
        # Створення UserProfile
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='Біографія')),
                ('avatar', models.BinaryField(blank=True, null=True, verbose_name='Аватар')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('follows', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL, verbose_name='Підписки')),
                ('interests', models.ManyToManyField(blank=True, to='webap.tag', verbose_name='Інтереси')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профіль користувача',
                'verbose_name_plural': 'Профілі користувачів',
            },
        ),
        # Додання обмежень
        migrations.AlterUniqueTogether(
            name='userinteraction',
            unique_together={('user', 'post', 'interaction_type')},
        ),
    ]
