# Generated by Django 4.1.3 on 2022-11-20 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='organizations',
            field=models.ManyToManyField(blank=True, to='core.organization'),
        ),
    ]
