# Generated by Django 3.1.2 on 2020-11-19 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0008_auto_20201119_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='precioportipo',
            name='alta',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AlterField(
            model_name='precioportipo',
            name='baja',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
    ]