# Generated by Django 5.1.1 on 2024-11-12 15:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0018_egreso_tipo_ingreso_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compras',
            name='id_caja',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='compras', to='stock.arqueocaja'),
        ),
    ]