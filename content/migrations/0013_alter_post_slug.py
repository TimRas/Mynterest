# Generated by Django 3.2.17 on 2023-02-15 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_alter_post_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(default='djangodbmodelsfieldscharfield', max_length=70, unique=True),
        ),
    ]