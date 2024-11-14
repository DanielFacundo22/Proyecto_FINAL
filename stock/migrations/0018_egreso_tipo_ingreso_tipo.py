# Generated by Django 5.1.1 on 2024-11-12 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0017_movimiento_descripcion_movimiento_tipo'),
    ]

    operations = [
        migrations.AddField(
            model_name='egreso',
            name='tipo',
            field=models.CharField(choices=[('manual', 'Manual'), ('compra', 'Compra')], default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ingreso',
            name='tipo',
            field=models.CharField(choices=[('manual', 'Manual'), ('venta', 'Venta')], default=1, max_length=50),
            preserve_default=False,
        ),
    ]