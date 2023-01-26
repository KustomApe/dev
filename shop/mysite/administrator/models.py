from django.db import models

# Create your models here.

class Admin(models.Model):

    admin_id = models.CharField(primary_key=True, max_length=128, unique=True) #PK
    password = models.CharField(max_length=256)

    def __str__(self):
        return self.admin_id #表示内容

    class Meta:
        ordering = ["-admin_id"] #並び順
        verbose_name = "管理者"
        verbose_name_plural = "管理者"