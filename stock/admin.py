from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ArqueoCaja
from .models import Proveedores
from .models import Clientes
from .models import Empleados
from .models import Productos
from .models import Ventas
from .models import det_ventas
from .models import Compras
from .models import det_compras

#CAJA
admin.site.register (ArqueoCaja)

#Proveedores
admin.site.register(Proveedores)

#Clientes
admin.site.register(Clientes)

#Empleados
admin.site.register(Empleados)

#Productos
admin.site.register(Productos)

#Ventas
admin.site.register(Ventas)

#det_venta
admin.site.register(det_ventas)

#Compras
admin.site.register(Compras)

#det_compras
admin.site.register(det_compras)

#ADMIN
class EmpleadosInline(admin.StackedInline):
    model = Empleados
    can_delete = False
    verbose_name_plural = 'Empleados'
class UserAdmin(BaseUserAdmin):
    inlines = (EmpleadosInline,)
# Desregistrar el UserAdmin original
admin.site.unregister(User)
# Registrar el nuevo UserAdmin
admin.site.register(User, UserAdmin)

