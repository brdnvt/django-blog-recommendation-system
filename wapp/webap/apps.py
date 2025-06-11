from django.apps import AppConfig


class WebapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webap'

class BlogConfig(AppConfig):
    name = 'blog'

    def ready(self):
        import blog.signals 