# Generated by Django 3.2 on 2023-06-26 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_auto_20230623_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='content.topic'),
        ),
    ]