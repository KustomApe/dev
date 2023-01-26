from django import forms

class UserForm(forms.Form):
    id = forms.CharField(label="会員ID", max_length=128)
    password = forms.CharField(label="パスワード", max_length=256, widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    id = forms.CharField(label="会員ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="パスワード", max_length=256, widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="パスワード(確認)", max_length=256, widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))
    name = forms.CharField(label="お名前", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(label="ご住所", max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))