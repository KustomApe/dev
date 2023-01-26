from django import forms
from . import models

class SearchForm(forms.Form):
    # product = forms.ModelChoiceField(models.Product.objects, label='商品')
    # amount = forms.IntegerField(min_value=1, max_value=10, label='個数')
    category = forms.ModelChoiceField(models.Category.objects.order_by('category_id'), label='カテゴリ', to_field_name="category_id", initial='0')
    keyword = forms.CharField(label="キーワード", max_length=128, required = False)