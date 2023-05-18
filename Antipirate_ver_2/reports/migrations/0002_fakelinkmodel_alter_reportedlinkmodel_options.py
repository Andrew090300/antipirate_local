# Generated by Django 4.1.6 on 2023-05-09 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FakeLinkModel',
            fields=[
                ('reportedlinkmodel_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='reports.reportedlinkmodel')),
            ],
            options={
                'verbose_name': 'Fake Link',
            },
            bases=('reports.reportedlinkmodel',),
        ),
        migrations.AlterModelOptions(
            name='reportedlinkmodel',
            options={'verbose_name': 'Reported Link'},
        ),
    ]