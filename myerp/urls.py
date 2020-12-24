"""myerp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('logout/', views.logout),

    path('test/', views.test),

    path('get_cli/', views.get_cli),
    path('get_sup/', views.get_sup),
    path('get_good/', views.get_good),

    path('supplier_list/', views.supplier_list),
    path('adv_list/', views.adv_list),
    path('supplier_add/', views.SupplierAdd.as_view()),
    path('supplier_edit/', views.supplier_edit),

    path('client_list/', views.client_list),
    path('debt_list/', views.debt_list),
    path('client_add/', views.ClientAdd.as_view()),
    path('client_edit/', views.client_edit),

    path('driver_list/', views.driver_list),
    path('driver_search/', views.driver_search),
    path('driver_add/', views.driver_add),
    path('driver_edit/', views.driver_edit),

    path('sale_list/', views.sale_list),
    path('sale_search/', views.sale_search),
    path('sale_add/', views.sale_add),
    path('sale_edit/', views.sale_edit),

    path('order_list/', views.order_list),
    path('order_add/', views.order_add),
    path('order_detal/', views.order_detal),
    path('order_del/', views.order_del),

    path('good_list/', views.good_list),
    path('good_add/', views.GoodAdd.as_view()),
    path('good_edit/', views.good_edit),

    path('payment_list/', views.payment_list),
    path('payment_add/', views.payment_add),
    path('payment_del/', views.payment_del),

    path('receipt_list/', views.receipt_list),
    path('receipt_add/', views.receipt_add),
    path('receipt_del/', views.receipt_del),

]
