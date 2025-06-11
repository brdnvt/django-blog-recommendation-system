from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import BlogPost

@receiver([post_save, post_delete], sender=BlogPost)
def clear_blogpost_cache(sender, instance, **kwargs):
    cache.delete('all_posts')
