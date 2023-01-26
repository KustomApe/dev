from django import forms
from account.models import User

class UserForm(forms.Form):
    id = forms.CharField(label="管理者ID", max_length=128)
    password = forms.CharField(label="パスワード", max_length=256, widget=forms.PasswordInput)

class RegisterForm(forms.Form):
    id = forms.CharField(label="管理者ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="パスワード", max_length=256, widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="パスワード(確認)", max_length=256, widget=forms.PasswordInput(render_value=True, attrs={'class': 'form-control'}))
    name = forms.CharField(label="お名前", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))

class UserSearchForm(forms.Form):
    # product = forms.ModelChoiceField(models.Product.objects, label='商品')
    # amount = forms.IntegerField(min_value=1, max_value=10, label='個数')
    # category = forms.ModelChoiceField(models.Category.objects.order_by('category_id'), label='カテゴリ', to_field_name="category_id", initial='0')
    keyword = forms.CharField(label="会員ID", max_length=128, required = False)

class PurchaseSearchForm(forms.Form):
    year = (
        ('2017', 2017),('2018', 2018), ('2019', 2019),('2020', 2020),('2021', 2021),
    )
    month = (
        ('1', 1),('2', 2),('3', 3),('4', 4),('5', 5),('6', 6),
        ('7', 7),('8', 8),('9', 9),('10', 10),('11', 11),('12', 12),
    )
    day = (
        ('1', 1),('2', 2),('3', 3),('4', 4),('5', 5),('6', 6),('7', 7),('8', 8),('9', 9),('10', 10),
        ('11', 11),('12', 12),('13', 13),('14', 14),('15', 15),('16', 16),('17', 17),('18', 18),('19', 19),('20', 20),
        ('21', 21),('22', 22),('23', 23),('24', 24),('25', 25),('26', 26),('27', 27),('28', 28),('29', 29),('30', 30),
        ('31', 31),
    )
    keyword = forms.CharField(label="会員ID", max_length=128, required = False)
    from_y = forms.ChoiceField(choices=year, initial=2019, widget=forms.widgets.Select)
    from_m = forms.ChoiceField(choices=month, initial=1)
    from_d = forms.ChoiceField(choices=day, initial=1)
    to_y = forms.ChoiceField(choices=year, initial=2020, widget=forms.widgets.Select)
    to_m = forms.ChoiceField(choices=month, initial=12)
    to_d = forms.ChoiceField(choices=day, initial=31)