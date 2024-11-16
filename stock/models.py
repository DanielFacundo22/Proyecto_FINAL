# stock/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

#CRUD
class Proveedores(models.Model):
    id_prov = models.AutoField(primary_key=True)
    nombre_prov = models.CharField(max_length=100, verbose_name="nombre del proveedor", null=False, blank=True)
    cuit_prov = models.CharField(max_length=100 ,verbose_name="cuit del proveedor",null=True, blank=True)
    tipo_prov = models.CharField(max_length=100,verbose_name="tipo de proveedor", null=True, blank=True)
    direcc_prov = models.CharField(max_length=100,verbose_name="direccion del proveedor", null=False)
    tel_prov = models.CharField(max_length=50,verbose_name="telefono del proveedor", null=True, blank=True)
    correo_prov = models.EmailField(max_length=100,verbose_name="email del proveedor", null=True, blank=True)

    def __str__(self):
        return self.nombre_prov
    
class Clientes(models.Model):
    id_cli=models.AutoField(primary_key=True)
    nombre_cli=models.CharField(max_length=100, verbose_name="Nombre del cliente",null=False)
    apellido_cli=models.CharField(max_length=100, verbose_name="Apellido del cliente", null=False)
    cuit_cli=models.CharField(max_length=100 ,verbose_name="cuit-dni del cliente", null=False)
    direcc_cli=models.CharField(max_length=100, verbose_name="Direccion del cliente", null=True, blank=True)
    tel_cli=models.CharField(max_length=50, verbose_name="Telefono del cliente", null=True, blank=True) 

    def __str__(self):
        return self.nombre_cli
    
class Empleados(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleado', null=True, blank=True)
    id_emplead = models.AutoField(primary_key=True)
    nombre_emplead = models.CharField(max_length=100, verbose_name="Nombre del empleado", null=False)
    apellido_emplead = models.CharField(max_length=100, verbose_name="Apellido del empleado", null=False)
    dni_emplead = models.CharField(max_length=100, verbose_name="DNI del empleado", null=False)
    direcc_emplead = models.CharField(max_length=100, verbose_name="Dirección del empleado", null=True, blank=True)
    tel_emplead = models.CharField(max_length=50, verbose_name="Teléfono del empleado", null=True, blank=True)
    correo_emplead = models.EmailField(max_length=100, verbose_name="Email del empleado", null=True, blank=True)
    sueldo_emplead = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Sueldo del empleado", null=True, blank=True)
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio", null=False)
    fecha_fin = models.DateField(verbose_name="Fecha de finalización", null=True, blank=True)

    def delete(self, *args, **kwargs):
        # Si el empleado tiene un usuario asociado, eliminarlo también
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)
        
    def __str__(self):
        return f"{self.nombre_emplead} {self.apellido_emplead}"

class AuditoriaEmpleado(models.Model):
    empleado = models.ForeignKey(Empleados, on_delete=models.CASCADE)
    nombre_empleado = models.CharField(max_length=255)
    proceso = models.CharField(max_length=255)
    fecha_hora = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nombre_empleado} - {self.proceso} - {self.fecha_hora}"
    
class Productos(models.Model):
    id_prod= models.AutoField(primary_key=True)
    id_prov=models.ForeignKey(Proveedores, on_delete=models.SET_NULL, null=True, blank=True, related_name="productos")
    nombre_prod=models.CharField(max_length=100, verbose_name="Nombre del Articulo", null=False)
    precio_costo=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de costo", null=True, blank=True)
    precio_prod=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio", null=False)
    stock_min=models.IntegerField(null=True, blank=True)
    stock_max=models.IntegerField(null=True, blank=True)
    stock_actual=models.IntegerField(null=True,blank=True)
    punto_reposicion=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return self.nombre_prod

#CAJA
class ArqueoCaja(models.Model):
    id_caja = models.AutoField(primary_key=True)
    id_emplead = models.ForeignKey('Empleados', on_delete=models.SET_NULL, null=True, related_name="cajas")
    fecha_hs_apertura = models.DateTimeField(verbose_name="Fecha y hora de apertura", null=False)
    fecha_hs_cierre = models.DateTimeField(verbose_name="Fecha y hora de cierre", null=True, blank=True) 
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_ingreso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ingreso total del día", null=True, blank=True)
    total_egreso = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Gastos del día", null=True, blank=True)
    cerrado = models.BooleanField(default=False)

    @classmethod
    def get_arqueo_abierto(cls, empleado):
        """Devuelve el arqueo abierto más reciente para un empleado."""
        return cls.objects.filter(id_emplead=empleado, cerrado=False).order_by('-fecha_hs_apertura').first()
    
    def save(self, *args, **kwargs):
        # Guarda primero si el objeto es nuevo (no tiene ID aún)
        if not self.pk:
            super().save(*args, **kwargs)

        # Recalcula montos solo si skip_calculation es False
        if not kwargs.pop('skip_calculation', False):
            self.calcular_montos()
        
        super().save(*args, **kwargs)

    def calcular_montos(self):
        """Calcula los totales de ingreso y egreso y actualiza el monto final."""
        self.total_ingreso = sum(ingreso.monto for ingreso in self.ingresos.all())
        self.total_egreso = sum(egreso.monto for egreso in self.egresos.all())
        self.monto_final = self.monto_inicial + self.total_ingreso - self.total_egreso
        # Guarda nuevamente los cambios
        self.save(skip_calculation=True)

    def cerrar_caja(self):
        self.total_ingreso = sum(ingreso.monto for ingreso in self.ingresos.all())
        self.total_egreso = sum(egreso.monto for egreso in self.egresos.all())
        self.monto_final = self.monto_inicial + self.total_ingreso - self.total_egreso
        self.cerrado = True
        self.fecha_hs_cierre = timezone.now()
        self.save()

    def __str__(self):
        return f"Caja de {self.id_emplead} - {self.id_caja} "

class Ingreso(models.Model):
    id_ingreso = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(ArqueoCaja, on_delete=models.CASCADE, related_name='ingresos')
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50, choices=[('manual', 'Manual'), ('venta', 'Venta')])
    def __str__(self):
        return f"Ingreso {self.id_ingreso} - {self.descripcion}"

class Egreso(models.Model):
    id_egreso = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(ArqueoCaja, on_delete=models.CASCADE, related_name='egresos')
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_egreso = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=50, choices=[('manual', 'Manual'), ('compra', 'Compra')])
    def __str__(self):
        return f"Egreso {self.id_egreso} - {self.descripcion}"

class Movimiento(models.Model):
    caja = models.ForeignKey(ArqueoCaja, on_delete=models.CASCADE, related_name='movimientos')
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50)  # Nuevo campo para el tipo de movimiento
    descripcion = models.CharField(max_length=255, null=True, blank=True)  # Campo opcional para la descripción

#COMPRA
class Compras(models.Model):
    id_compra=models.AutoField(primary_key=True)
    id_prov=models.ForeignKey(Proveedores, on_delete=models.SET_NULL, null=True, blank=True, related_name="compras")
    id_caja=models.ForeignKey(ArqueoCaja, on_delete=models.SET_NULL, null=True, related_name="compras")
    fecha_compra=models.DateField(verbose_name="Fecha de compra", null=False)
    total_compra=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de la compra", null=False)
    descrip_compra=models.CharField(max_length=150, verbose_name="Agregue un comentario", null=True, blank=True)

    def __str__(self):
        return f"Compra: {self.id_compra}"
    
class det_compras(models.Model):
    id_det_compra=models.AutoField(primary_key=True)
    id_compra=models.ForeignKey(Compras, on_delete=models.SET_NULL, null=True, blank=True, related_name="det_compras")
    id_prod=models.ForeignKey(Productos, on_delete=models.SET_NULL, null=True, blank=True, related_name="det_compras")
    cant_comprada=models.IntegerField(verbose_name="Cantidad unitaria", null=False)
    precio_unitario=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio", null=False)
    subtotal_compra=models.DecimalField(max_digits=10, decimal_places=2, null=False)
    
    def __str__(self):
        return f"det_venta: {self.id_det_compra}"

#VENTA
class Ventas(models.Model):
    id_venta=models.AutoField(primary_key=True)
    id_caja=models.ForeignKey(ArqueoCaja, on_delete=models.SET_NULL, null=True, related_name="ventas")
    id_cli=models.ForeignKey(Clientes, on_delete=models.SET_NULL, null=True,blank=True, related_name="ventas")
    fecha_hs=models.DateTimeField(null=False)
    total_venta=models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de la venta",null=False)

    def __str__(self):
        return f"Venta: {self.id_venta}"

class det_ventas(models.Model):
    id_det_venta=models.AutoField(primary_key=True)
    id_prod=models.ForeignKey(Productos, on_delete=models.SET_NULL,null= True, blank=True, related_name="det_ventas" )
    id_venta=models.ForeignKey(Ventas, on_delete=models.SET_NULL, null=True, blank=True, related_name="det_ventas")
    precio_prod=models.DecimalField(max_digits=10, decimal_places=2,null=False, verbose_name="Precio")
    subtotal_venta=models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name="Subtotal")
    cant_vendida=models.IntegerField(null=False, verbose_name="Cantidad")

    def __str__(self):
        return f"det_venta: {self.id_det_venta}"
    



