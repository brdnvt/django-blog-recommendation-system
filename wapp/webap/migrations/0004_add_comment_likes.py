# Generated by Django 4.2.7 on 2025-06-11 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("webap", "0003_auto_20250611_1942"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="blogpost",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Блог пост",
                "verbose_name_plural": "Блог пости",
            },
        ),
        migrations.AlterModelOptions(
            name="postcomment",
            options={
                "ordering": ["-last_modified"],
                "verbose_name": "Коментар",
                "verbose_name_plural": "Коментарі",
            },
        ),
        migrations.AddField(
            model_name="postcomment",
            name="likes_count",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Кількість лайків"
            ),
        ),
        migrations.AlterField(
            model_name="blogpost",
            name="post_picture",
            field=models.BinaryField(
                blank=True, null=True, verbose_name="Зображення допису"
            ),
        ),
    ]
