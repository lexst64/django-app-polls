# Generated by Django 4.0.2 on 2022-02-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_author',
            field=models.CharField(default='', max_length=200),
        ),
    ]
