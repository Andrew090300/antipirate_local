# Generated by Django 4.1.6 on 2023-05-09 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='parsedlink',
            name='fake_links',
            field=models.BooleanField(default=False),
        ),
    ]