#!/usr/bin/env python
"""
Скрипт для створення тестових даних для блог-системи
"""
import os
import sys
import django

# Налаштування Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wapp.settings')
django.setup()

from django.contrib.auth.models import User
from webap.models import Category, Tag, BlogPost, PostComment, UserProfile, UserInteraction

def create_test_data():
    print("Створення тестових даних...")
    
    # Створення суперкористувача
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("✓ Створено суперкористувача: admin/admin123")
    
    # Створення тестових користувачів
    test_users = [
        ('john_doe', 'john@example.com', 'password123'),
        ('jane_smith', 'jane@example.com', 'password123'),
        ('bob_wilson', 'bob@example.com', 'password123'),
    ]
    
    users = []
    for username, email, password in test_users:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username, email, password)
            user.first_name = username.split('_')[0].title()
            user.last_name = username.split('_')[1].title() if '_' in username else ''
            user.save()
            users.append(user)
            print(f"✓ Створено користувача: {username}")
        else:
            users.append(User.objects.get(username=username))
    
    # Створення категорій
    categories_data = [
        ('Технології', 'tech', 'Статті про новітні технології', '#007bff'),
        ('Програмування', 'programming', 'Уроки та поради з програмування', '#28a745'),
        ('Дизайн', 'design', 'Статті про веб-дизайн та UX/UI', '#fd7e14'),
        ('Наука', 'science', 'Наукові дослідження та відкриття', '#6f42c1'),
        ('Стиль життя', 'lifestyle', 'Поради щодо здорового способу життя', '#e83e8c'),
    ]
    
    categories = []
    for name, slug, description, color in categories_data:
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'description': description, 'color': color}
        )
        if created:
            print(f"✓ Створено категорію: {name}")
        categories.append(category)
    
    # Створення тегів
    tags_data = [
        ('Python', 'python', '#3776ab'),
        ('Django', 'django', '#092e20'),
        ('JavaScript', 'javascript', '#f7df1e'),
        ('React', 'react', '#61dafb'),
        ('AI', 'ai', '#ff6b6b'),
        ('ML', 'ml', '#4ecdc4'),
        ('WebDev', 'webdev', '#45b7d1'),
        ('Tutorial', 'tutorial', '#96ceb4'),
        ('Tips', 'tips', '#ffeaa7'),
        ('News', 'news', '#fd79a8'),
    ]
    
    tags = []
    for name, slug, color in tags_data:
        tag, created = Tag.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'color': color}
        )
        if created:
            print(f"✓ Створено тег: {name}")
        tags.append(tag)
    
    # Створення блог-постів
    posts_data = [
        {
            'title': 'Введення в Django для початківців',
            'text': '''Django - це високорівневий веб-фреймворк Python, який заохочує швидкий розвиток і чистий, прагматичний дизайн. 
            
В цій статті ми розглянемо основи Django, як почати працювати з фреймворком, і створимо простий веб-додаток.

## Що таке Django?

Django - це безкоштовний веб-фреймворк з відкритим кодом, написаний на Python. Він дотримується архітектурного шаблону model-view-template (MVT) і призначений для полегшення створення складних, керованих базами даних веб-сайтів.

## Основні переваги Django:

1. **Швидка розробка** - Django включає багато готових компонентів
2. **Безпека** - Django допомагає уникнути багатьох поширених помилок безпеки
3. **Масштабованість** - Django може обробляти трафік від високих до дуже високих обсягів
4. **Універсальність** - Django можна використовувати для створення майже будь-якого типу веб-сайту

Почніть вивчати Django сьогодні!''',
            'category': categories[1],  # Програмування
            'tags': [tags[0], tags[1], tags[7]],  # Python, Django, Tutorial
            'author': users[0] if users else User.objects.first(),
        },
        {
            'title': 'Сучасні тренди у веб-дизайні 2025',
            'text': '''Веб-дизайн постійно еволюціонує, і 2025 рік не є винятком. Розглянемо найактуальніші тренди цього року.

## Головні тренди:

### 1. Мінімалізм та чистота
Чистий, мінімалістичний дизайн залишається популярним. Менше елементів означає кращу фокусування на контенті.

### 2. Темні теми
Темні теми не тільки виглядають сучасно, але й зменшують навантаження на очі користувачів.

### 3. Адаптивний дизайн
Мобільні пристрої складають більше 60% трафіку, тому адаптивність критично важлива.

### 4. Мікроанімації
Невеликі анімації покращують користувацький досвід та роблять інтерфейс більш живим.

### 5. Персоналізація
AI дозволяє створювати персоналізований контент для кожного користувача.

Слідкуйте за трендами, але пам'ятайте - зручність користувача завжди на першому місці!''',
            'category': categories[2],  # Дизайн
            'tags': [tags[6], tags[8]],  # WebDev, Tips
            'author': users[1] if len(users) > 1 else User.objects.first(),
        },
        {
            'title': 'Штучний інтелект у повсякденному житті',
            'text': '''Штучний інтелект вже не є науковою фантастикою - він навколо нас і змінює наше повсякденне життя.

## Де ми зустрічаємо AI щодня:

### Персональні асистенти
Siri, Google Assistant, Alexa - вони допомагають нам керувати розумним домом, знаходити інформацію та планувати день.

### Соціальні мережі
Алгоритми визначають, який контент ми бачимо у стрічці новин Facebook, Instagram, TikTok.

### Онлайн-покупки
Рекомендаційні системи Amazon, Netflix, Spotify використовують AI для персоналізації.

### Транспорт
GPS-навігація, оптимізація маршрутів, автономне водіння - усе це AI.

### Охорона здоров'я
Діагностика захворювань, аналіз медичних зображень, розробка ліків.

## Майбутнє AI

Експерти прогнозують, що AI стане ще більш інтегрованим у наше життя. Важливо розуміти ці технології та їх вплив на суспільство.

Готуйтеся до майбутнього з AI!''',
            'category': categories[3],  # Наука
            'tags': [tags[4], tags[5], tags[9]],  # AI, ML, News
            'author': users[2] if len(users) > 2 else User.objects.first(),
        },
        {
            'title': 'React Hooks: повний посібник',
            'text': '''React Hooks революціонізували спосіб написання компонентів React. Розглянемо основні хуки та їх використання.

## Що таке React Hooks?

Hooks дозволяють використовувати стан та інші можливості React без написання класових компонентів.

## Основні хуки:

### useState
```javascript
const [count, setCount] = useState(0);
```

### useEffect
```javascript
useEffect(() => {
  document.title = `Count: ${count}`;
}, [count]);
```

### useContext
```javascript
const theme = useContext(ThemeContext);
```

### useReducer
```javascript
const [state, dispatch] = useReducer(reducer, initialState);
```

## Кастомні хуки

Ви можете створювати власні хуки для переваристування логіки:

```javascript
function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });
  
  const setValue = (value) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.log(error);
    }
  };
  
  return [storedValue, setValue];
}
```

Hooks роблять код більш читабельним та дозволяють легше ділитися логікою між компонентами!''',
            'category': categories[1],  # Програмування
            'tags': [tags[2], tags[3], tags[7]],  # JavaScript, React, Tutorial
            'author': users[0] if users else User.objects.first(),
        },
        {
            'title': '10 корисних порад для продуктивності',
            'text': '''Хочете бути більш продуктивними? Ось 10 перевірених порад, які допоможуть вам досягти більшого.

## 1. Техніка Помодоро
Працюйте 25 хвилин, потім робіть 5-хвилинну перерву. Повторіть 4 рази, потім зробіть довшу перерву.

## 2. Планування з вечора
Плануйте наступний день ввечері. Це допоможе вам почати ранок з чіткими цілями.

## 3. Правило 2 хвилин
Якщо завдання займає менше 2 хвилин - зробіть його зараз.

## 4. Елімінуйте відволікання
Вимкніть сповіщення, закрийте зайві вкладки, створіть фокусне середовище.

## 5. Використовуйте матриці Ейзенхауера
Поділіть завдання на: важливі/термінові, важливі/не термінові, не важливі/термінові, не важливі/не термінові.

## 6. Групуйте схожі завдання
Відповідайте на всі емейли одразу, робіть всі дзвінки підряд.

## 7. Встановлюйте дедлайни
Навіть для завдань без чітких термінів встановлюйте власні дедлайни.

## 8. Делегуйте
Не намагайтеся робити все самостійно. Делегуйте те, що можуть зробити інші.

## 9. Вчіться говорити "ні"
Кожне "так" одному завданню - це "ні" іншому. Будьте вибірковими.

## 10. Піклуйтеся про себе
Добрий сон, здорове харчування та фізичні вправи - основа продуктивності.

Почніть з одного-двох порад і поступово впроваджуйте інші!''',
            'category': categories[4],  # Стиль життя
            'tags': [tags[8], tags[9]],  # Tips, News
            'author': users[1] if len(users) > 1 else User.objects.first(),
        },
    ]
    
    created_posts = []
    for post_data in posts_data:
        if not BlogPost.objects.filter(title=post_data['title']).exists():
            tags_for_post = post_data.pop('tags')
            post = BlogPost.objects.create(**post_data)
            post.tags.set(tags_for_post)
            created_posts.append(post)
            print(f"✓ Створено пост: {post.title}")
    
    # Створення профілів користувачів
    for user in User.objects.all():
        if not UserProfile.objects.filter(user=user).exists():
            profile = UserProfile.objects.create(
                user=user,
                bio=f"Привіт! Я {user.first_name}. Захоплююсь технологіями та люблю ділитися знаннями."
            )
            # Додамо випадкові інтереси
            if tags:
                profile.interests.set(tags[:3])
            print(f"✓ Створено профіль для: {user.username}")
    
    # Створення тестових взаємодій
    if created_posts and users:
        for i, post in enumerate(created_posts[:3]):
            for j, user in enumerate(users[:2]):
                if user != post.author:
                    # Лайки
                    UserInteraction.objects.get_or_create(
                        user=user,
                        post=post,
                        interaction_type='like'
                    )
                    # Перегляди
                    UserInteraction.objects.get_or_create(
                        user=user,
                        post=post,
                        interaction_type='view'
                    )
        
        # Оновимо лічильники
        for post in created_posts:
            likes_count = UserInteraction.objects.filter(post=post, interaction_type='like').count()
            views_count = UserInteraction.objects.filter(post=post, interaction_type='view').count()
            post.likes_count = likes_count
            post.views_count = views_count + 10  # Додаємо деякі базові перегляди
            post.save()
        
        print("✓ Створено тестові взаємодії")
    
    # Створення тестових коментарів
    comments_data = [
        "Дуже корисна стаття! Дякую за детальне пояснення.",
        "Чудові поради! Обов'язково спробую застосувати.",
        "Цікаво, а які ще є альтернативи?",
        "Супер! Саме те, що я шукав.",
        "Дякую за поділ досвідом!",
    ]
    
    if created_posts and users:
        for i, comment_text in enumerate(comments_data):
            if i < len(created_posts):
                user = users[i % len(users)]
                post = created_posts[i]
                if user != post.author:
                    PostComment.objects.get_or_create(
                        author=user,
                        post=post,
                        text=comment_text
                    )
        print("✓ Створено тестові коментарі")
    
    print("\n🎉 Тестові дані успішно створені!")
    print(f"📊 Статистика:")
    print(f"  - Користувачі: {User.objects.count()}")
    print(f"  - Категорії: {Category.objects.count()}")
    print(f"  - Теги: {Tag.objects.count()}")
    print(f"  - Пости: {BlogPost.objects.count()}")
    print(f"  - Коментарі: {PostComment.objects.count()}")
    print(f"  - Взаємодії: {UserInteraction.objects.count()}")
    print(f"  - Профілі: {UserProfile.objects.count()}")
    print("\n🚀 Тепер ви можете увійти як admin/admin123 або створити нового користувача!")

if __name__ == '__main__':
    create_test_data()
