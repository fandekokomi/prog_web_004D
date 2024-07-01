from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from django_recaptcha.fields import ReCaptchaField
from django.contrib.auth.forms import ReadOnlyPasswordHashField

class ArtistaForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Artista
        fields = '__all__'
        widgets = {
            'fecha_nacimiento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

class ProductoForm(forms.ModelForm):
    captcha = ReCaptchaField()

    tipo = forms.ModelChoiceField(queryset=TipoProducto.objects.all())
    def __init__(self, *args, **kwargs):
        super(ProductoForm, self).__init__(*args, **kwargs)
        self.fields['artista'].queryset = Artista.objects.filter(habilitado=True)
        self.fields['artista'].empty_label = "Seleccione un artista"

    class Meta:
        model = Producto
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Las contraseñas no son visibles aquí. "
            "Puede cambiar la contraseña usando "
            "<a href=\"../password/\">este formulario</a>."
        ),
    )

    class Meta:
        model = Usuario
        fields = '__all__'

    def clean_password(self):
        return self.initial["password"]

class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'tipo_usuario')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class SolicitudPForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = SolicitudP
        fields = ['nombre_producto', 'descripcion_producto', 'imagen_producto', 'tipo_producto', 'precio_producto', 'artista_producto']
        widgets = {
            'artista_producto': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(SolicitudPForm, self).__init__(*args, **kwargs)
        self.fields['artista_producto'].queryset = Artista.objects.filter(habilitado=True)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class SolicitudAForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = SolicitudA
        fields = ['nombre_artista', 'fecha_nacimiento_artista', 'biografia_artista', 'imagen_artista', 'sitio_web_artista',]
        widgets = {
            'fecha_nacimiento_artista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'imagen_artista': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super(SolicitudAForm, self).__init__(*args, **kwargs)

class SolicitudesRechazadasAForm(forms.ModelForm):
    captcha = ReCaptchaField()
    solicitud_tipo = forms.CharField(initial='A', widget=forms.HiddenInput())

    class Meta:
        model = SolicitudesRechazadas
        fields = ['solicitudA', 'mensaje_rechazo', 'solicitud_tipo']
        widgets = {
            'solicitudA': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtén la ID de la solicitud del ciclo actual
        solicitud_actual = kwargs.get('initial', {}).get('solicitudA')
        # Establece las opciones del combobox
        self.fields['solicitudA'].widget.choices = [(solicitud_actual, solicitud_actual)]

class SolicitudesRechazadasPForm(forms.ModelForm):
    captcha = CaptchaField()
    solicitud_tipo = forms.CharField(initial='B', widget=forms.HiddenInput())

    class Meta:
        model = SolicitudesRechazadas
        fields = ['solicitudP', 'mensaje_rechazo', 'solicitud_tipo']
        widgets = {
            'solicitudP': forms.Select(attrs={'class': 'form-select', 'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtén la ID de la solicitud del ciclo actual
        solicitud_actual = kwargs.get('initial', {}).get('solicitudP')
        # Establece las opciones del combobox
        self.fields['solicitudP'].widget.choices = [(solicitud_actual, solicitud_actual)]

class AprobarSolicitudForm(forms.Form):
    captcha = ReCaptchaField()
    solicitud_id = forms.IntegerField(widget=forms.HiddenInput())

class registerForm(UserCreationForm):
    captcha = CaptchaField()
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']

class MiembroForm(forms.ModelForm):
    captcha = ReCaptchaField()
    usuario = forms.ModelChoiceField(queryset=Usuario.objects.all(), disabled=True)
    password = forms.CharField(
        label="Actualizar Contraseña", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese la nueva contraseña del miembro'}), 
        required=False,
        help_text="""
        <ul>
            <li>La contraseña no puede asemejarse tanto a la otra información personal del miembro.</li>
            <li>La contraseña debe contener al menos 8 caracteres.</li>
            <li>La contraseña no puede ser una clave utilizada comúnmente.</li>
            <li>La contraseña no puede ser completamente numérica.</li>
        </ul>
        """
    )

    class Meta:
        model = Usuario
        fields = ['usuario', 'password']

    def __init__(self, *args, **kwargs):
        super(MiembroForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['usuario'].initial = self.instance.pk
            self.fields['password'].widget.attrs['value'] = ''

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Debes ingresar una contraseña.")
        try:
            validate_password(password, self.instance)
        except ValidationError as e:
            raise forms.ValidationError(e.messages)
        return password

