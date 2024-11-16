from django import forms
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
import string
import secrets

#PROVEEDORES
class ProveedoresForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        fields = "__all__"

#CLIENTES
class ClientesForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields="__all__"

#EMPLEADOS
class EmpleadosForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False)

    class Meta:
        model = Empleados
        fields = ['nombre_emplead', 'apellido_emplead', 'dni_emplead', 'direcc_emplead',
                  'tel_emplead', 'correo_emplead', 'sueldo_emplead', 'fecha_inicio']

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        if self.instance and self.instance.user:
            initial = kwargs.setdefault('initial', {})
            initial['username'] = self.instance.user.username
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            user_query = User.objects.filter(username=username)
            if self.instance and self.instance.user:
                user_query = user_query.exclude(id=self.instance.user.id)

            if user_query.exists():
                raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def generar_clave_aleatoria(self, longitud=5):
        caracteres = string.digits
        clave_aleatoria = ''.join(secrets.choice(caracteres) for _ in range(longitud))
        return clave_aleatoria

    def save(self, commit=True):
        empleado = super().save(commit=False)

        # Generar clave aleatoria
        password = self.generar_clave_aleatoria()

        if self.cleaned_data.get('username'):
            if self.instance and self.instance.user:
                # Actualizar usuario existente
                user = self.instance.user
                user.username = self.cleaned_data['username']
                user.set_password(password)  
            else:
                
                user = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    password=password,
                    email=self.cleaned_data['correo_emplead']
                )
            user.save()
            empleado.user = user

        if commit:
            empleado.save()

        
        send_mail(
            'Tu nueva cuenta ha sido registrada',
            f'Tu usuario y clave de acceso es:{user} {password}',
            'rabatrix_bp@outlook.es',  
            [self.cleaned_data['correo_emplead']],
            fail_silently=False,
        )

        return empleado

##PRODUCTOS
class ProductosForm(forms.ModelForm):
    class Meta:
        model = Productos
        fields = ['nombre_prod', 'precio_prod', 'stock_min', 'stock_max', 'stock_actual', 'punto_reposicion'] 

    def clean_nombre_prod(self):
        nombre_prod = self.cleaned_data.get('nombre_prod')
        if not nombre_prod:
            raise forms.ValidationError("El nombre del artículo es obligatorio.")
        return nombre_prod

    def clean_precio_prod(self):
        precio_prod = self.cleaned_data.get('precio_prod')
        if precio_prod is None or precio_prod < 0:
            raise forms.ValidationError("El precio debe ser un número positivo.")
        return precio_prod

    def clean_stock_min(self):
        stock_min = self.cleaned_data.get('stock_min')
        if stock_min is not None and stock_min < 0:
            raise forms.ValidationError("El stock mínimo no puede ser negativo.")
        return stock_min


    def clean_stock_max(self):
        stock_max = self.cleaned_data.get('stock_max')
        if stock_max is not None and stock_max < 0:
            raise forms.ValidationError("El stock máximo no puede ser negativo.")
        return stock_max

    def clean_stock_actual(self):
        stock_actual = self.cleaned_data.get('stock_actual')
        if stock_actual is not None and stock_actual < 0:
            raise forms.ValidationError("El stock actual no puede ser negativo.")
        return stock_actual

    def clean_punto_reposicion(self):
        punto_reposicion = self.cleaned_data.get('punto_reposicion')
        if punto_reposicion is not None and punto_reposicion < 0:
            raise forms.ValidationError("El punto de reposición no puede ser negativo.")
        return punto_reposicion

#VENTAS
class VentasForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields=["id_caja","id_cli", "total_venta", "fecha_hs"]

#COMPRAS
class ComprasForm(forms.ModelForm):
    class Meta:
        model = Compras
        fields=["id_compra","id_prov","id_caja","fecha_compra","total_compra"]

#CAJA
class ArqueoCajaForm(forms.ModelForm):
    class Meta:
        model = ArqueoCaja
        fields = ['id_emplead', 'monto_inicial']

    def __init__(self, *args, **kwargs):
        super(ArqueoCajaForm, self).__init__(*args, **kwargs)
        self.fields['id_emplead'].widget = forms.HiddenInput()

    def clean_monto_inicial(self):
        monto_inicial = self.cleaned_data.get('monto_inicial')
        if monto_inicial < 0:
            raise forms.ValidationError("El monto inicial no puede ser negativo.")
        return monto_inicial
    
class CerrarArqueoForm(forms.ModelForm):
    class Meta:
        model = ArqueoCaja
        fields = []

class IngresoForm(forms.ModelForm):
    class Meta:
        model = Ingreso
        fields = ['descripcion', 'monto']
        widgets = {
            'descripcion': forms.TextInput(attrs={'style': 'width: 400px;'}),
            'monto': forms.NumberInput(attrs={'style': 'width: 100px;'}),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return monto

class EgresoForm(forms.ModelForm):
    class Meta:
        model = Egreso
        fields = ['descripcion', 'monto']
        widgets = {
            'descripcion': forms.TextInput(attrs={'style': 'width: 400px;'}),
            'monto': forms.NumberInput(attrs={'style': 'width: 100px;'}),
        }

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto < 0:
            raise forms.ValidationError("El monto no puede ser negativo.")
        return monto 


class SeleccionarCajaForm(forms.Form):
    caja = forms.ModelChoiceField(
        queryset=ArqueoCaja.objects.filter(cerrado=False),  # Solo cajas abiertas
        label="Seleccionar Caja",
        empty_label="Seleccione una caja"
    )
