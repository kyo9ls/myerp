# Generated by Django 2.2.1 on 2020-12-20 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20201220_2054'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='good',
            unique_together={('name', 'supplier')},
        ),
    ]
