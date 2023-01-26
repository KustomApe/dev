from django.db import models
from datetime import datetime
# Create your models here.

class Category(models.Model):
    category_id = models.IntegerField(primary_key=True, unique=True) #PK
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name #表示内容
    class Meta:
        ordering = ["-category_id"] #並び順
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"

class Item(models.Model):
    item_id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=128)
    manufacturer = models.CharField(max_length=32)
    color = models.CharField(max_length=16)
    price = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    recommended = models.BooleanField(default=False)
    category = models.ForeignKey('Category',on_delete=models.CASCADE,) #外部キー
    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-item_id"]
        verbose_name = "商品"
        verbose_name_plural = "商品"

class ItemsInCart(models.Model):
    user = models.ForeignKey('account.User',on_delete=models.CASCADE) #外部キー
    item = models.ForeignKey('Item', on_delete=models.CASCADE) #外部キー
    amount = models.IntegerField()
    booked_date = models.DateTimeField(auto_now_add=True) #自動生成
    def __str__(self):
        return self.user.user_id + 'のカート-' + self.item.name
    class Meta:
        ordering = ["-booked_date"]
        verbose_name = "ショッピングカート"
        verbose_name_plural = "ショッピングカート"

class Purchase(models.Model):
    purchase_id = models.IntegerField(primary_key=True, unique=True) #PK
    user = models.ForeignKey('account.User',on_delete=models.CASCADE,) #外部キー
    destination = models.CharField(max_length=256)
    booked_date = models.DateTimeField(auto_now_add=True)
    # booked_date = models.DateTimeField(default=datetime.now)

    cancel = models.BooleanField(default=False)
    def __str__(self):
        return self.user.user_id + 'が' + self.booked_date.strftime('%Y-%m-%d %H:%M') + 'に注文した'
    class Meta:
        ordering = ["-booked_date"]
        verbose_name = "購入履歴"
        verbose_name_plural = "購入履歴"

class PurchaseDetail(models.Model):
    purchase_detail_id = models.IntegerField(primary_key=True, unique=True) #PK
    purchase = models.ForeignKey('Purchase',on_delete=models.CASCADE,) #外部キー
    item = models.ForeignKey('Item',on_delete=models.CASCADE,) #外部キー
    amount = models.IntegerField()
    def __str__(self):
        return str(self.purchase.purchase_id) + '注文-' + self.item.name
    class Meta:
        ordering = ["-purchase_detail_id"]
        verbose_name = "注文詳細"
        verbose_name_plural = "注文詳細"