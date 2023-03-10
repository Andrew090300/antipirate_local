# Generated by Django 4.1.6 on 2023-02-13 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('music', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParsedLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('link', models.URLField(max_length=1024, unique=True)),
                ('domain', models.CharField(blank=True, max_length=256, null=True)),
                ('blocked', models.BooleanField(default=False)),
                ('reports_num', models.IntegerField(default=0)),
                ('checked', models.BooleanField(default=False)),
                ('music_found', models.BooleanField(default=False)),
                ('music_links', models.TextField(blank=True, null=True)),
                ('manual_check', models.BooleanField(default=False)),
                ('music_match', models.BooleanField(default=False)),
                ('music', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='music.musicmodel')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
