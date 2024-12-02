from django.forms import widgets, MultipleChoiceField, CheckboxSelectMultiple, ModelChoiceField
from django.forms import ModelForm, ValidationError, forms, DateInput, DateField, MultipleChoiceField
from django.contrib.auth.forms import AuthenticationForm
from django.forms.fields import CharField, EmailField
from django.forms.widgets import NumberInput
from django import forms

from hotel.models import Hotel, PrecioPorTipo, TemporadaAlta, Habitacion, PaqueteTuristico
from core.models import Servicio, TipoHabitacion, Vendedor, Persona



class HotelForm(ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'
        exclude = ['servicios', 'tipos', 'vendedores']
        # Debemos quitar vendedores de aca ya que nosotros tenemos un crear vendedor
        # y asignar vendedor a hotel

    def __init__(self, *args, **kwargs):
        super(HotelForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['localidad'].widget.attrs.update({'class': 'form-control'})
        self.fields['direccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['encargado'].widget.attrs.update({'class': 'form-control'})
        self.fields['categoria'].widget.attrs.update({'class': 'form-control'})


class TemporadaHotelForm(ModelForm):
    class Meta:
        model = TemporadaAlta
        fields = '__all__'
        exclude = ['hotel']
        widgets = {
            'inicio': DateInput(attrs={'id':'fecha1','type': 'date','min':'','value':'', 'onclick':'fecha_actual();'}),
            'fin': DateInput(attrs={'id':'fecha2','type': 'date','min':'','value':'', 'onclick':'fecha_minima();'})
        }

    def __init__(self, *args, **kwargs):
        super(TemporadaHotelForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['inicio'].widget.attrs.update({'class': 'form-control'})
        self.fields['fin'].widget.attrs.update({'class': 'form-control'})
   
class PaqueteTuristicoForm(forms.ModelForm):
    habitaciones = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = PaqueteTuristico
        fields = '__all__'
        exclude = ['hotel', 'vendido', 'precio']
        widgets = {
            'inicio': forms.DateInput(attrs={'id': 'fecha1', 'type': 'date', 'min': '', 'value': '', 'onclick': 'fecha_actual();'}),
            'fin': forms.DateInput(attrs={'id': 'fecha2', 'type': 'date', 'min': '', 'value': '', 'onclick': 'fecha_minima();'})
        }

    def __init__(self, *args, **kwargs):
        super(PaqueteTuristicoForm, self).__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['coeficiente'].widget.attrs.update({'class': 'form-control', 'min':'0', 'max':'1'})
        self.fields['inicio'].widget.attrs.update({'class': 'form-control'})
        self.fields['fin'].widget.attrs.update({'class': 'form-control'})
        self.fields['habitaciones'].widget.attrs.update({'class': 'form-control'})
        


class AgregarTipoAHotelForm(ModelForm):
    class Meta:
        model = PrecioPorTipo
        fields = '__all__'
        exclude = ['hotel']

    def __init__(self, *args, **kwargs):
        super(AgregarTipoAHotelForm, self).__init__(*args, **kwargs)
        self.fields['tipo'].widget.attrs.update({'class': 'form-control'})
        self.fields['baja'].widget.attrs.update({'class': 'form-control' ,'min': '0' ,'required': 'required'})
        self.fields['alta'].widget.attrs.update({'class': 'form-control' ,'min': '0' ,'required': 'required'})

    def clean(self):
            cleaned_data = super(AgregarTipoAHotelForm, self).clean()
            baja = cleaned_data.get('baja')
            alta = cleaned_data.get('alta')

            if baja is not None and baja < 0:
                self.add_error('baja', 'El valor debe ser igual o mayor que 0.')

            if alta is not None and alta < 0:
                self.add_error('alta', 'El valor debe ser igual o mayor que 0.')

            return cleaned_data

class HabitacionForm(ModelForm):
    class Meta:
        model = Habitacion
        fields='__all__'
        exclude=['hotel','baja']
      
        
     
    def __init__(self, *args, **kwargs):
        super(HabitacionForm, self).__init__(*args, **kwargs)
        self.fields['numero'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo'].widget.attrs.update({'class': 'form-control'})
        

class VendedorHotelForm(forms.Form):
    vendedores = ModelChoiceField(queryset=Vendedor.objects.none())
    def __init__(self,colVendedores,hotel):
        super(VendedorHotelForm, self).__init__()
        self.fields['vendedores'].queryset = Vendedor.objects.all().exclude(hotel=hotel)
        self.fields['vendedores'].widget.attrs.update({'class': 'form-control'})

class ServicioForm(forms.Form):
    SERVICIO_CHOICES=(Servicio.objects.all())
    servicio = MultipleChoiceField(choices = SERVICIO_CHOICES)

