# Generated by Django 3.2 on 2023-04-21 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0016_auto_20230421_1330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='body',
            field=models.TextField(max_length=250),
        ),
        migrations.AlterField(
            model_name='post',
            name='excerpt',
            field=models.TextField(),
        ),
    ]