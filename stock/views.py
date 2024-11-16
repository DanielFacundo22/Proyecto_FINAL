from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.template.loader import get_template
from django.db.models import Sum, Value, CharField, F, Case, When, ExpressionWrapper, Func
from .models import *
from .forms import *
from datetime import date, datetime, timedelta
from xhtml2pdf import pisa 
from itertools import chain
from operator import attrgetter

#INICIO
@login_required
def inicio(request):
    producto=Productos.objects.all()
    return render (request, "inicio.html",{"productos":producto})

#SESIONES
def procesar_login(request):    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('inicio')  
        else:
            messages.error(request, "Usuario o contraseña incorrecta")  
    return render(request, "procesar_login.html")

@login_required
def cerrar_sesion(request):
    if ArqueoCaja.objects.filter(cerrado=False).exists():
        arqueo_abierto = get_object_or_404(ArqueoCaja, cerrado=False)
        return redirect('cerrar_arqueo', id_caja=arqueo_abierto.id_caja)

    logout(request)
    return redirect('procesar_login')

#CAJA
@login_required
def apertura_arqueo(request):
    if request.user.is_staff:  # Verifica si el usuario tiene permisos de administrador
        messages.error(request, "No tienes un empleado asociado para abrir una caja.")
        return redirect('historial_arqueo')

    try:
        empleado = request.user.empleado
    except Empleados.DoesNotExist:
        messages.error(request, "No tienes un empleado asociado para abrir una caja.")
        return redirect('historial_arqueo')

    if ArqueoCaja.objects.filter(id_emplead=empleado, cerrado=False).exists():
        messages.error(request, "Ya tienes una caja abierta. No puedes abrir otra hasta que la actual esté cerrada.")
        return redirect('historial_arqueo')

    if request.method == 'POST':
        form = ArqueoCajaForm(request.POST)
        if form.is_valid():
            arqueo = form.save(commit=False)
            arqueo.id_emplead = empleado
            arqueo.fecha_hs_apertura = timezone.now()
            arqueo.monto_final = 0  # Inicialmente 0
            arqueo.total_ingreso = 0
            arqueo.total_egreso = 0
            
            # Guarda el arqueo para asignar un ID antes de operaciones relacionadas
            arqueo.save()

            # **Registrar el movimiento de apertura para el arqueo**
            Movimiento.objects.create(
                caja=arqueo,  # Relacionado con el arqueo
                tipo='APERTURA',
                monto=arqueo.monto_inicial,  # El monto de apertura
                descripcion='Apertura de caja'
            )
            
            # Recalcular montos por seguridad (si hay algún ingreso/egreso inicial)
            arqueo.calcular_montos()

            return redirect('historial_arqueo')
    else:
        form = ArqueoCajaForm(initial={'id_emplead': empleado})

    return render(request, 'caja/apertura_arqueo.html', {'form': form})


@login_required
def cerrar_arqueo(request, id_caja):
    # Obtener el registro de la caja o devolver un error 404 si no existe
    arqueo = get_object_or_404(ArqueoCaja, id_caja=id_caja)

    # Validar si el usuario tiene un empleado relacionado o es superusuario
    if request.user.is_superuser:
            messages.error(request, "No tienes un empleado asociado para cerrar esta caja.")
            return redirect('historial_arqueo')

    # Verificar que la caja pertenece al empleado que está haciendo la solicitud
    if arqueo.id_emplead != request.user.empleado:
        messages.error(request, "No tienes permiso para cerrar esta caja.")
        return redirect('historial_arqueo')

    if request.method == 'POST':
        form = CerrarArqueoForm(request.POST, instance=arqueo)
        if form.is_valid():
            # Al cerrar la caja, calcular el monto final
            arqueo.cerrar_caja()
            return redirect('historial_arqueo')
    else:
        form = CerrarArqueoForm(instance=arqueo)

    return render(request, 'caja/cerrar_arqueo.html', {'form': form, 'arqueo': arqueo})

@login_required
def historial_arqueo(request):
    fecha_apertura = request.GET.get('fecha_apertura')

    if fecha_apertura:
        try:
            start_date = datetime.strptime(fecha_apertura, '%Y-%m-%d')
            end_date = start_date + timedelta(days=1)
            arqueos = ArqueoCaja.objects.filter(
                fecha_hs_apertura__gte=start_date,
                fecha_hs_apertura__lt=end_date
            ).order_by('-fecha_hs_apertura')
        except ValueError:
            arqueos = ArqueoCaja.objects.all().order_by('-fecha_hs_apertura')
    else:
        arqueos = ArqueoCaja.objects.prefetch_related('ingresos', 'egresos', 'ventas').order_by('-fecha_hs_apertura')

    # Recalcula los montos para cada arqueo cargado
    for arqueo in arqueos:
        arqueo.calcular_montos()

    return render(request, 'caja/historial_arqueo.html', {'arqueos': arqueos, 'fecha_apertura': fecha_apertura})



@login_required
def movimientos_arqueo(request, caja_id):
    caja = get_object_or_404(ArqueoCaja, id_caja=caja_id)
    
    # Movimientos generales (incluyendo apertura de caja)
    movimientos = Movimiento.objects.filter(caja=caja).annotate(
        tipo_literal=Case(
            When(descripcion='Apertura de caja', then=Value('Apertura de caja', output_field=CharField())),
            default=Value('Movimiento', output_field=CharField())
        ),
        fecha_movimiento=F('fecha'),
        monto_calculado=F('monto')
    ).order_by('-fecha')

    # Ingresos manuales para el arqueo específico
    ingresos = Ingreso.objects.filter(id_caja=caja, tipo='manual').annotate(
        tipo_literal=Value('Ingreso', output_field=CharField()),
        fecha_movimiento=F('fecha_ingreso'),
        monto_calculado=F('monto')
    ).order_by('-fecha_ingreso')

    # Egresos manuales para el arqueo específico
    egresos = Egreso.objects.filter(id_caja=caja).annotate(
        tipo_literal=Value('Egreso', output_field=CharField()),
        fecha_movimiento=F('fecha_egreso'),
        monto_calculado=F('monto')
    ).order_by('-fecha_egreso')

    # Ventas para el arqueo específico
    ventas = Ventas.objects.filter(id_caja=caja).annotate(
        tipo_literal=Value('Venta', output_field=CharField()),
        fecha_movimiento=F('fecha_hs'),
        detalle=Func(
            Value('Venta '), F('id_venta'),
            function='CONCAT',
            output_field=CharField()
        ),
        monto_calculado=F('total_venta')
    ).order_by('-fecha_hs')

    # Unir todos los movimientos y ordenarlos por fecha
    movimientos_unificados = sorted(
        chain(movimientos, ingresos, egresos, ventas),
        key=attrgetter('fecha_movimiento'),
        reverse=True
    )

    return render(request, 'caja/movimientos_arqueo.html', {
        'caja': caja,
        'movimientos': movimientos_unificados,
    })


@login_required
def obtener_monto_final(request, id_caja):
    arqueo = ArqueoCaja.objects.get(id=id_caja)
    arqueo.calcular_montos()
    return JsonResponse({
        'monto_final': arqueo.monto_final,
        'total_ingreso': arqueo.total_ingreso,
        'total_egreso': arqueo.total_egreso,
    })

#INGRESO Y EGRESO
@login_required
def registrar_ingreso(request):
    if request.user.is_superuser:
        # Superusuario: Selecciona una caja abierta y registra el ingreso.
        if request.method == 'POST':
            seleccionar_caja_form = SeleccionarCajaForm(request.POST)
            form = IngresoForm(request.POST)

            if seleccionar_caja_form.is_valid() and form.is_valid():
                arqueo_abierto = seleccionar_caja_form.cleaned_data['caja']  # Caja seleccionada
                ingreso = form.save(commit=False)
                ingreso.id_caja = arqueo_abierto  # Asocia el ingreso con la caja seleccionada
                ingreso.tipo = 'manual'
                ingreso.save()

                # Recalcula montos de la caja seleccionada
                arqueo_abierto.calcular_montos()

                messages.success(
                    request,
                    f"Ingreso registrado con éxito en la caja de {arqueo_abierto.id_emplead.nombre_emplead}."
                )
                return redirect('historial_arqueo')
        else:
            seleccionar_caja_form = SeleccionarCajaForm()
            form = IngresoForm()

        return render(request, 'transacciones/registrar_ingreso.html', {
            'form': form,
            'seleccionar_caja_form': seleccionar_caja_form
        })

    # Empleado: Operación normal.
    empleado = request.user.empleado
    arqueo_abierto = ArqueoCaja.get_arqueo_abierto(empleado)
    if not arqueo_abierto:
        messages.error(request, "No tienes una caja abierta. Debes abrir una caja primero.")
        return redirect('historial_arqueo')

    if request.method == 'POST':
        form = IngresoForm(request.POST)
        if form.is_valid():
            ingreso = form.save(commit=False)
            ingreso.id_caja = arqueo_abierto
            ingreso.tipo = 'manual'
            ingreso.save()
            arqueo_abierto.calcular_montos()
            messages.success(request, f"Ingreso registrado con éxito en tu caja.")
            return redirect('historial_arqueo')
    else:
        form = IngresoForm()

    return render(request, 'transacciones/registrar_ingreso.html', {
        'form': form,
        'arqueo_abierto': arqueo_abierto
    })

@login_required
def registrar_egreso(request):
    if request.user.is_superuser:
        # Superusuario: Selecciona una caja abierta y registra el egreso.
        if request.method == 'POST':
            seleccionar_caja_form = SeleccionarCajaForm(request.POST)
            form = EgresoForm(request.POST)

            if seleccionar_caja_form.is_valid() and form.is_valid():
                arqueo_abierto = seleccionar_caja_form.cleaned_data['caja']  # Caja seleccionada
                egreso = form.save(commit=False)
                egreso.id_caja = arqueo_abierto  # Asocia el egreso con la caja seleccionada
                egreso.tipo = 'manual'
                egreso.save()

                # Recalcula montos de la caja seleccionada
                arqueo_abierto.calcular_montos()

                messages.success(
                    request,
                    f"Egreso registrado con éxito en la caja de {arqueo_abierto.id_emplead.nombre_emplead}."
                )
                return redirect('historial_arqueo')
        else:
            seleccionar_caja_form = SeleccionarCajaForm()
            form = EgresoForm()

        return render(request, 'transacciones/registrar_egreso.html', {
            'form': form,
            'seleccionar_caja_form': seleccionar_caja_form
        })

    # Empleado: Operación normal.
    empleado = request.user.empleado
    arqueo_abierto = ArqueoCaja.get_arqueo_abierto(empleado)
    if not arqueo_abierto:
        messages.error(request, "No tienes una caja abierta. Debes abrir una caja primero.")
        return redirect('historial_arqueo')

    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            egreso = form.save(commit=False)
            egreso.id_caja = arqueo_abierto
            egreso.tipo = 'manual'
            egreso.save()
            arqueo_abierto.calcular_montos()
            messages.success(request, f"Egreso registrado con éxito en tu caja.")
            return redirect('historial_arqueo')
    else:
        form = EgresoForm()

    return render(request, 'transacciones/registrar_egreso.html', {
        'form': form,
        'arqueo_abierto': arqueo_abierto
    })


#PRODUCTOS
@login_required
def mostrar_articulos(request):
    producto=Productos.objects.all()
    return render(request, "articulos/mostrar.html",{"productos":producto})

@permission_required('stock.view_articulo')
def editar_articulos(request,id_prod):
    producto = Productos.objects.get(id_prod=id_prod)
    formulario = ProductosForm(request.POST or None, request.FILES or None, instance=producto)

    if request.method == 'POST':
        if formulario.is_valid():  
            formulario.save()  
            messages.success(request, "Artículo editado exitosamente.")  
            return redirect('mostrar_articulos') 

    return render(request, "articulos/editar.html", {"formulario": formulario})

@login_required
def crear_articulos(request):
    formulario = ProductosForm(request.POST or None)
    if request.method == 'POST':  # 
        if formulario.is_valid():
            formulario.save()
            return redirect("mostrar_articulos")
    return render(request, "articulos/crear.html", {"formulario": formulario})

@permission_required('stock.view_articulo')
def eliminar_productos(request,id_prod):
    producto = Productos.objects.get(id_prod=id_prod)
    producto.delete()
    return redirect("mostrar_articulos")

#CLIENTES
def mostrar_clientes(request):
    cliente=Clientes.objects.all()
    return render(request, "clientes/mostrar.html",{"clientes":cliente})


def editar_clientes(request, id_cli):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar provedores")
        return redirect('mostrar_clientes')
    cliente = Clientes.objects.get(id_cli=id_cli)
    formulario = ClientesForm(request.POST or None, request.FILES or None, instance=cliente)
    
    if request.method == 'POST':
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente editado exitosamente.")
            return redirect('mostrar_clientes') 

    return render(request, "clientes/editar.html", {"formulario": formulario})

def crear_clientes(request):
    formulario = ClientesForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect("mostrar_clientes")
    return render(request,"clientes/crear.html",{"formulario": formulario})


def eliminar_clientes(request, id_cli):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar provedores")
        return redirect('mostrar_clientes')
    cliente = Clientes.objects.get(id_cli=id_cli)
    cliente.delete()
    return redirect("mostrar_clientes")

#EMPLEADOS
@login_required
def mostrar_empleados(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver la lista de empleados")
        return redirect('inicio')
    empleado=Empleados.objects.all()
    return render(request,"empleados/mostrar.html",{"empleados":empleado})

@permission_required('stock.view_empleado')
def editar_empleados(request, id_emplead):
    # Obtener el empleado o devolver 404 si no existe
    empleado = get_object_or_404(Empleados, id_emplead=id_emplead)
    
    # Crear el formulario con los datos existentes del empleado
    formulario = EmpleadosForm(request.POST or None, request.FILES or None, instance=empleado)

    # Si el formulario es válido, guardamos los cambios
    if formulario.is_valid():
        formulario.save()  # Guarda los cambios del empleado en la base de datos
        messages.success(request, 'Datos personales del empleado actualizados correctamente.')
        return redirect('mostrar_empleados')  # Redirigir a la lista de empleados

    # Renderizamos la página de edición si es GET o el formulario no es válido
    return render(request, "empleados/editar.html", {"formulario": formulario, "empleado": empleado})

@permission_required('stock.view_empleado')
def crear_empleados(request):
    formulario = EmpleadosForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect("mostrar_empleados")
    return render(request, "empleados/crear.html", {"formulario": formulario})

@permission_required('stock.view_empleado')
def eliminar_empleados(request, id_emplead):
    empleado = Empleados.objects.get(id_emplead=id_emplead)
    empleado.delete()
    messages.success(request, "Empleado y usuario eliminados correctamente.")
    return redirect("mostrar_empleados")

@login_required 
def ver_acciones_empleado(request, empleado_id):
    # Obtener el empleado especificado
    empleado = get_object_or_404(Empleados, id_emplead=empleado_id)
    # Filtrar las acciones de auditoría para este empleado
    acciones = AuditoriaEmpleado.objects.filter(empleado=empleado).order_by('-fecha_hora')

    context = {
        'empleado': empleado,
        'acciones': acciones
    }
    return render(request, 'ver_acciones.html', context)

@login_required
def registrar_accion(empleado, proceso):
    AuditoriaEmpleado.objects.create(
        empleado=empleado,
        nombre_empleado=f"{empleado.nombre_emplead} {empleado.apellido_emplead}",
        proceso=proceso,
        fecha_hora=timezone.now()
    )

#PROVEDORES
@login_required
def mostrar_proveedores(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver la lista de proveedores")
        return redirect('inicio')

    proveedor= Proveedores.objects.all()
    return render(request, "proveedores/mostrar.html",{"proveedores": proveedor})

@login_required
@permission_required('stock.view_empleado')
def editar_proveedores(request, id_prov):
   
    proveedor = get_object_or_404(Proveedores, id_prov=id_prov)
    

    formulario = ProveedoresForm(request.POST or None, request.FILES or None, instance=proveedor)

    if formulario.is_valid():
        formulario.save()  
        messages.success(request, 'Proveedor actualizado correctamente.')
        return redirect('mostrar_proveedores')  
    
   
    return render(request, "proveedores/editar.html", {"formulario": formulario})

@permission_required('stock.view_empleado')
def crear_proveedores(request):
    formulario = ProveedoresForm(request.POST or None)
    if formulario.is_valid ():
     formulario.save()
     return redirect("mostrar_proveedores")
    return render(request, "proveedores/crear.html", {"formulario": formulario})

@permission_required('stock.view_empleado')
def eliminar_proveedores(request,id_prov):
    proveedor = Proveedores.objects.get(id_prov=id_prov)
    proveedor.delete()
    return redirect("mostrar_proveedores")

#VENTA
@login_required
def crear_venta(request):
    producto = Productos.objects.all()
    cliente = Clientes.objects.all()
    
    # Obtener el empleado actual
    try:
        empleado_actual = Empleados.objects.get(user=request.user)
    except Empleados.DoesNotExist:
        messages.error(request, "No tienes un empleado asociado para hacer ventas.")
        return redirect('inicio')
    
    # Obtener el arqueo abierto para el empleado actual
    arqueo_abierto = ArqueoCaja.objects.filter(id_emplead=empleado_actual, cerrado=False).first()

    if not arqueo_abierto:
        messages.error(request, "No tienes una caja abierta. Debes abrir una caja primero.")
        return redirect('apertura_arqueo')

    # Validar si el usuario es administrador
    if request.user.is_staff:
        messages.error(request, "No tienes un empleado asociado para hacer ventas.")
        return redirect('inicio')

    if request.method == "POST":
        id_cli = request.POST.get('cliente')
        total_venta = request.POST.get('total')

        cliente_obj = Clientes.objects.get(id_cli=id_cli) if id_cli else None

        nueva_venta = Ventas(
            id_caja=arqueo_abierto,  # Asociar venta al arqueo de caja abierto del empleado actual
            id_cli=cliente_obj,
            total_venta=total_venta,
            fecha_hs=timezone.now()
        )
        nueva_venta.save()

        registrar_accion(empleado_actual, f"Creación de venta {nueva_venta.id_venta}")

        productos_ids = request.POST.getlist('productos[]')
        cantidades = request.POST.getlist('cantidades[]')
        subtotales = request.POST.getlist('subtotales[]')

        for i in range(len(productos_ids)):
            producto = Productos.objects.get(id_prod=productos_ids[i])
            cantidad = int(cantidades[i])
            subtotal = float(subtotales[i])

            if cantidad > producto.stock_actual:
                messages.error(request, f"Stock insuficiente para el producto {producto.nombre_prod}. Disponible: {producto.stock_actual}.")
                return redirect("crear_venta")

            nuevo_detalle = det_ventas(
                id_prod=producto,
                id_venta=nueva_venta,
                precio_prod=producto.precio_prod,
                subtotal_venta=subtotal,
                cant_vendida=cantidad
            )
            nuevo_detalle.save()

            registrar_accion(empleado_actual, f"Creación de detalle de venta para producto {producto.nombre_prod}")

            producto.stock_actual -= cantidad
            producto.save()

        # Registrar automáticamente el ingreso en el arqueo de caja
        nuevo_ingreso = Ingreso(
            id_caja=arqueo_abierto,
            descripcion=f"Venta {nueva_venta.id_venta}",
            monto=total_venta
        )
        nuevo_ingreso.save()

        registrar_accion(empleado_actual, f"Registro de ingreso en arqueo para venta {nueva_venta.id_venta}")

        # Actualizar los montos en el arqueo de caja
        arqueo_abierto.calcular_montos()

        registrar_accion(empleado_actual, f"Actualización de montos en arqueo de caja {arqueo_abierto.id_caja}")

        return redirect('det_venta', id_venta=nueva_venta.id_venta)

    else:
        formulario = VentasForm()

    context = {
        "empleados": Empleados.objects.all(),
        "clientes": cliente,
        "productos": producto,
        "formulario": formulario
    }
    return render(request, "ventas/crear_venta.html", context)


@login_required
def det_venta(request, id_venta):
    venta = get_object_or_404(Ventas, id_venta=id_venta)
    detalles = det_ventas.objects.filter(id_venta=venta)

    context = {
        'venta': venta,
        'detalles': detalles
    }
    return render(request, 'ventas/detalle_ventas.html', context)

@login_required
def GenerarPdf(request,id_venta ):
    venta=Ventas.objects.get(id_venta=id_venta)
    detalles=det_ventas.objects.filter(id_venta=venta)
    context={
        "venta":venta,
        "detalles":detalles,
    }
    template =get_template("ventas/detalle_ventas_pdf.html")
    html=template.render(context)
    
    response=HttpResponse(content_type="aplication/pdf")
    response["content-disposition"]=f'attachment; filename="DetalleVenta_{venta.id_venta}.pdf"'

    pisa_status= pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse(f"error: {pisa_status.err}")
    return response

@login_required
def historial_ventas(request):
    ventas=Ventas.objects.all().order_by("-fecha_hs")
    context={
        "ventas": ventas
    }
    return render (request, "ventas/historial_ventas.html", context)

@login_required
def ventas_del_mes(request):
    ventas = (
        Ventas.objects
        .filter(fecha_hs__month=date.today().month, fecha_hs__year=date.today().year)  # Cambiado a fecha_hs
        .values('fecha_hs')  # Cambiado a fecha_hs
        .annotate(total=Sum('total_venta'))
        .order_by('fecha_hs') 
    )

    labels = [venta['fecha_hs'].strftime('%d-%m') for venta in ventas]  # Cambiado a fecha_hs
    data = [venta['total_venta'] for venta in ventas]

    return JsonResponse({'labels': labels, 'data': data})

#COMPRAS   
@login_required
def crear_compra(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar compras.")
        return redirect('inicio')
     
    proveedores = Proveedores.objects.all()
    productos = Productos.objects.all()

    if request.method == "POST":
        id_prov = request.POST.get("proveedor")
        total_compra = request.POST.get("total")
        proveedor = get_object_or_404(Proveedores, id_prov=id_prov)
        
       

        # Crear la compra principal
        nueva_compra = Compras(
            id_prov=proveedor,
            fecha_compra=timezone.now(),
            total_compra=total_compra,
            descrip_compra=request.POST.get("descrip_compra")
        )
        nueva_compra.save()

        # Procesar los detalles de la compra
        producto_ids = request.POST.getlist('producto_ids[]')
        cantidades = request.POST.getlist('cantidades[]')
        precios_costos = request.POST.getlist('precios_costos[]')

        for i in range(len(producto_ids)):
            id_producto = producto_ids[i]
            cantidad = int(cantidades[i])
            precio_costo = float(precios_costos[i])
            subtotal = cantidad * precio_costo

            producto = get_object_or_404(Productos, id_prod=id_producto)
            producto.precio_costo = precio_costo
            producto.stock_actual+=cantidad
            producto.save()

            det_compra = det_compras(
                id_compra=nueva_compra,
                id_prod=producto,
                cant_comprada=cantidad,
                precio_unitario=precio_costo,
                subtotal_compra=subtotal
            )
            det_compra.save()

        return redirect('det_compra', id_compra=nueva_compra.id_compra)

    context = {
        "proveedores": proveedores,
        "productos": productos
    }

    return render(request, "compras/crear_compra.html", context)

@login_required
def det_compra(request, id_compra):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para visualizar historial de compra.")
        return redirect('inicio')
    
    # Obtener la compra específica
    compra = get_object_or_404(Compras, id_compra=id_compra)
    # Obtener todos los detalles de productos asociados a esta compra
    detalles = det_compras.objects.filter(id_compra=compra)

    context = {
        'compra': compra,
        'detalles': detalles,
    }
    return render(request, 'compras/det_compras.html', context)

@login_required
@permission_required("stock.view_empleado")
def historial_compra(request):
    # Obtener todas las compras ordenadas por fecha (la más reciente primero)
    compras = Compras.objects.all().order_by('-fecha_compra')

    context = {
        'compras': compras,
    }
    return render(request, 'compras/historial_compras.html', context)


