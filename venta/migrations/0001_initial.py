# Generated by Django 3.1.1 on 2020-09-18 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hotel', '0001_initial'),
        ('core', '0002_auto_20200918_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='Liquidacion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('abonado', models.DateField(null=True)),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.vendedor')),
            ],
        ),
        migrations.CreateModel(
            name='Factura',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.cliente')),
                ('liquidacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='venta.liquidacion')),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.vendedor')),
            ],
        ),
        migrations.CreateModel(
            name='Alquiler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_huespedes', models.PositiveSmallIntegerField()),
                ('inicio', models.DateField()),
                ('fin', models.DateField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
                ('factura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alquileres', to='venta.factura')),
                ('habitaciones', models.ManyToManyField(to='hotel.Habitacion')),
                ('paquete', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hotel.paqueteturistico')),
            ],
        ),
    ]