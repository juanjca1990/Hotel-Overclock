from django.forms import ModelForm, forms, DateInput, DateField, MultipleChoiceField
from django.contrib.auth.forms import AuthenticationForm
from django.forms.fields import CharField, EmailField, IntegerField
from django.forms.widgets import NumberInput
from core.models import Vendedor, Persona, Cliente
from venta.models import Factura




class ClienteForm(ModelForm):
            
    class Meta: 
        model = Persona
        fields = '__all__'
        exclude = [ 'usuario' ]
    
    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})   
        self.fields['apellido'].widget.attrs.update({'class': 'form-control'})
        self.fields['documento'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_documento'].widget.attrs.update({'class': 'form-control'})


