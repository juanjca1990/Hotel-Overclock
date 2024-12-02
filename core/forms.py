from django.forms import ModelForm,MultipleChoiceField, CheckboxSelectMultiple, forms, ValidationError
from django.forms import widgets, MultipleChoiceField, CheckboxSelectMultiple
from core.models import Localidad, Pais, Provincia, Persona, TipoHabitacion, Servicio, Categoria, Vendedor, Encargado
from django.contrib.auth.forms import AuthenticationForm
from django.forms.fields import CharField, EmailField

# 
class PaisForm(ModelForm):
    class Meta:
        model = Pais
        fields = ['nombre']
   
    
    def __init__(self, *args, **kwargs):
        super(PaisForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control', 'placeholder':'Ingrese Nombre Pais', 'title':'Ingrese mas de tres caracteres, no deje en blanco'})

    def clean_nombre(self):
         nombreRecibido = self.cleaned_data.get("nombre")
         if nombreRecibido == '':
           raise ValidationError('Este nombre no esta permitido')
         if nombreRecibido.split(' ') == ' ':
           raise ValidationError('El nombre no puede estar vacio')
         return nombreRecibido
   
        

class ProvinciaForm(ModelForm):
    class Meta:
        model = Provincia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProvinciaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})


class LocalidadForm(ModelForm):
    class Meta:
        model = Localidad
        fields = '__all__'
        

    def __init__(self, *args, **kwargs):
        super(LocalidadForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        

class AutenticacionForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AutenticacionForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su usuario'})
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Ingrese su Clave'})
        self.fields['username'].label = ''
        self.fields['password'].label = ''

class TipoHabitacionForm(ModelForm):
    class Meta:
        model=TipoHabitacion
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(TipoHabitacionForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control'})
        self.fields['pasajeros'].widget.attrs.update({'class': 'form-control'})
        self.fields['cuartos'].widget.attrs.update({'class': 'form-control'})

class ServicioForm(ModelForm):
    class Meta:
        model=Servicio
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super(ServicioForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control'})

class CategoriaForm(ModelForm):
    class Meta:
        model=Categoria
        fields = '__all__'

       
    def __init__(self, *args, **kwargs):
        super(CategoriaForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['estrellas'].widget.attrs.update({'class': 'form-control'})
        self.fields['servicios'].widget.attrs.update({'class': 'form-check-input form-check-label posicion-checkbox'})
        self.fields['servicios'].choices=[(c.pk,c.nombre) for c in Servicio.objects.all()]

    servicios = MultipleChoiceField(
         widget=CheckboxSelectMultiple,        
     )

class VendedorForm(ModelForm):
    email = EmailField(label='email')
    usuario = CharField(label='nombre de usuario')
    contrasenia = CharField(label='contraseña')
    email.widget.attrs.update({'class': 'form-control'})
    usuario.widget.attrs.update({'class': 'form-control'})
    contrasenia.widget.attrs.update({'class': 'form-control'})
    
    class Meta: 
        model = Persona
        fields = '__all__'
        exclude = [ 'usuario' ]
    
    def __init__(self, *args, **kwargs):
        super(VendedorForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['apellido'].widget.attrs.update({'class': 'form-control'})
        self.fields['documento'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_documento'].widget.attrs.update({'class': 'form-control'})

#user_name, email, password

class EncargadoForm(ModelForm):
    clave = CharField(label='Clave')
    class Meta: 
        model = Persona
        fields = '__all__'
        exclude = [ 'usuario' ]

    def __init__(self, *args, **kwargs):
        super(EncargadoForm, self).__init__(*args, **kwargs)
        
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['apellido'].widget.attrs.update({'class': 'form-control'})
        self.fields['documento'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_documento'].widget.attrs.update({'class': 'form-control'})
        self.fields['clave'].widget.attrs.update({'class': 'form-control'})

        
        
    
    

