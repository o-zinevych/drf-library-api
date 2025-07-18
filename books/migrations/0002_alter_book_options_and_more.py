# Generated by Django 5.2.3 on 2025-06-29 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["title", "author"]},
        ),
        migrations.AddConstraint(
            model_name="book",
            constraint=models.UniqueConstraint(
                fields=("title", "author"), name="unique_title_and_author_combination"
            ),
        ),
    ]
