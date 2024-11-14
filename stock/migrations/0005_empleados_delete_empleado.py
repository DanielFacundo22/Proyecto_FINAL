# Generated by Django 5.1 on 2024-09-04 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_clientes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Empleados',
            fields=[
                ('id_emplead', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_emplead', models.CharField(max_length=100, verbose_name='Nombre del empelado')),
                ('apellido_emplead', models.CharField(max_length=100, verbose_name='Apellido del empleado')),
                ('dni_emplead', models.IntegerField(verbose_name='DNI del empleado')),
                ('direcc_emplead', models.CharField(blank=True, max_length=100, null=True, verbose_name='Direccion del empleado')),
                ('tel_emplead', models.CharField(blank=True, max_length=50, null=True, verbose_name='Telefono del empleado')),
                ('correo_emplead', models.CharField(blank=True, max_length=100, null=True, verbose_name='Email del empleado')),
                ('sueldo_emplead', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Sueldo del empleado')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de inicio')),
                ('fecha_fin', models.DateField(blank=True, null=True, verbose_name='Fecha de finalizacion')),
            ],
        ),
        migrations.DeleteModel(
            name='Empleado',
        ),
    ]