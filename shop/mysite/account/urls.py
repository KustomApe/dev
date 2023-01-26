from django.urls import path
from . import views

app_name = "account"

urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('registerUser/', views.register_user),
    path('registerUserCommit/', views.register_user_commit),
    path('userInfo/', views.user_info),
    path('updateUser/', views.update_user),
    path('updateUserCommit/', views.update_user_commit),
    path('withdraw/', views.withdraw),
    path('withdrawCommit/', views.withdraw_commit),
]