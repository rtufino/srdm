from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from .models import Usuario, Informe, ValidarFirma


class UsuarioCreateForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'username', 'email')


class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'username', 'email')

class FirmaForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ('archivo',)
class ValidarFirmaForm(forms.ModelForm):
    class Meta:
        model=ValidarFirma
        fields=('documento_id',)
