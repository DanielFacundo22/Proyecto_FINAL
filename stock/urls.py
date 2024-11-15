from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    ##Inicio
    path('inicio/', views.inicio, name='inicio'),

    ##Login
    path('procesar_login/', views.procesar_login, name='login'),
    path('', RedirectView.as_view(url='procesar_login/', permanent=True)),
    path('logout/', LogoutView.as_view(next_page="login"), name='logout'),

    ##CAJA
    path('apertura/', views.apertura_arqueo, name='apertura_arqueo'),
    path('historial/', views.historial_arqueo, name='historial_arqueo'),
    path('cerrar/<int:id_caja>/', views.cerrar_arqueo, name='cerrar_arqueo'),
    path('obtener_monto_final/<int:id_caja>/', views.obtener_monto_final, name='obtener_monto_final'),
    path('movimiento/<int:caja_id>/', views.movimientos_arqueo, name="movimientos_arqueo"),
    path('registrar_ingreso/', views.registrar_ingreso, name='registrar_ingreso'),
    path('registrar_egreso/', views.registrar_egreso, name='registrar_egreso'),
    
    ##CRUD Articulos
    path('mostrar_articulos/', views.mostrar_articulos, name='mostrar_articulos'),
    path("editar_articulos", views.editar_articulos, name="editar_articulos"),
    path("editar_articulos/<int:id_prod>/", views.editar_articulos, name="editar_articulos"),
    path("crear_articulos", views.crear_articulos, name="crear_articulos"),
    path("eliminar_producto/<int:id_prod>",views.eliminar_productos, name="eliminar_producto"),

    ##CRUD Clientes
    path('mostrar_clientes/', views.mostrar_clientes, name='mostrar_clientes'),
    path("editar_clientes/",views.editar_clientes, name="editar_clientes"),
    path("editar_clientes/<int:id_cli>/",views.editar_clientes, name="editar_clientes"),
    path("crear_clientes", views.crear_clientes, name="crear_clientes"),
    path("eliminar_clientes/<int:id_cli>",views.eliminar_clientes, name="eliminar_clientes"),

    ##CRUD Proveedores
    path("mostrar_proveedores",views.mostrar_proveedores ,name="mostrar_proveedores"),
    path("editar_proveedores",views.editar_proveedores ,name="editar_proveedores"),
    path("editar_proveedores/<int:id_prov>",views.editar_proveedores ,name="editar_proveedores"),
    path("crear_proveedores",views.crear_proveedores ,name="crear_proveedores"),
    path("eliminar_proveedores/<int:id_prov>",views.eliminar_proveedores, name="eliminar_proveedores" ),
    
    ##CRUD Empleados
    path("mostrar_empleados",views.mostrar_empleados, name="mostrar_empleados"),
    path("editar_empleados", views.editar_empleados, name="editar_empleados"),
    path("editar_empleados/<int:id_emplead>", views.editar_empleados, name="editar_empleados"),
    path("editar_empleados", views.editar_empleados, name="editar_empleados"),
    path("crear_empleados", views.crear_empleados, name="crear_empleados"),
    path("eliminar_empleados/<int:id_emplead>",views.eliminar_empleados, name="eliminar_empleados"),
    path("auditoria/empleado/<int:empleado_id>/", views.ver_acciones_empleado, name="ver_acciones_empleados"),

    ##Compras
    path("crear_compra",views.crear_compra,name="crear_compra"),
    path ("historial_compras", views.historial_compra, name="historial_compras"),
    path('compras/detalle/<int:id_compra>/', views.det_compra, name='det_compra'),
    
    ##Ventas
    path("crear_venta",views.crear_venta, name="crear_venta"),
    path('det_venta/<int:id_venta>/', views.det_venta, name='det_venta'),
    path('detalle_venta/pdf/<int:id_venta>/', views.GenerarPdf, name='generar_pdf'),
    path("historial_ventas", views.historial_ventas, name="historial_ventas"),
    path('ventas_del-mes/', views.ventas_del_mes, name='ventas_del_mes'),
 
]
