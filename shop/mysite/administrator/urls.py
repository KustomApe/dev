from django.urls import path
from . import views

app_name = "administrator"

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout),
    path('registerAdmin/', views.register_admin),
    path('', views.Index.as_view(), name='index'),
    path('list/', views.ItemList.as_view(), name='item_list'),
    path('add/', views.ItemCreate.as_view(), name='item_add'),
    path('update/<int:pk>/', views.ItemUpdate.as_view(), name='item_update'),
    path('delete/<int:pk>/', views.ItemDelete.as_view(), name='item_delete'),
    path('item_detail/<int:pk>/', views.ItemDetail.as_view(), name='item_detail'),
    path('userlist/', views.UserList.as_view(), name='user_list'),
    path('userupdate/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),
    path('userdelete/<int:pk>/', views.UserDelete.as_view(), name='user_delete'),
    path('purchaselist/', views.PurchaseList.as_view(), name='purchase_list'),
    path('purchsedelete/<int:pk>/', views.PurchaseDelete.as_view(), name='purchase_delete'),
]