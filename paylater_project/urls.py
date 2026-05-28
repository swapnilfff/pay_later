"""
URL configuration for paylater_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

urlpatterns = [
    path('admin/', admin.site.urls),
]

from django.contrib import admin
from django.urls import path
from core import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.index),
    path('register/', views.register),
    path('login/', views.login_view),

    path('dashboard/', views.dashboard),

    path('logout/', views.logout_view),

    path('admin-login/', views.admin_login),

    path('admin-dashboard/', views.admin_dashboard),

    path('merchant-requests/', views.merchant_requests),

    path('approve/<int:id>/', views.approve_merchant),

    path('reject/<int:id>/', views.reject_merchant),

    path('admin-logout/', views.admin_logout),

    path('customers/', views.customers),

    path('add-customer/', views.add_customer),

    path('edit-customer/<int:id>/',views.edit_customer),

    path('delete-customer/<int:id>/',views.delete_customer),

    path('ledger/<int:id>/',views.ledger),

    path('add-credit/<int:id>/',views.add_credit),

    path('add-payment/<int:id>/',views.add_payment),

    path('export-pdf/<int:id>/',views.export_pdf),

    path('notifications/',views.notifications),

    path('search-customer/',views.search_customer),

]

urlpatterns += static(settings.MEDIA_URL,
document_root=settings.MEDIA_ROOT)