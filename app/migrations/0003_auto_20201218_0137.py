# Generated by Django 2.2.1 on 2020-12-17 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20201217_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='remark',
            field=models.CharField(max_length=255, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='order',
            name='buying_price',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='进价'),
        ),
        migrations.AlterField(
            model_name='order',
            name='goods_price',
            field=models.DecimalField(decimal_places=2, max_digits=5, verbose_name='售价'),
        ),
    ]
