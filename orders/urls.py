from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='orders/login.html'), name='login'),
    path('profile/<str:client_name>/', views.profile, name='profile'),
    path('payment_history/<str:client_name>/', login_required(views.PaymentHistoryView.as_view(), login_url='login'), name='payment_history'),
    path('order_history/<str:client_name>/', login_required(views.OrderHistoryView.as_view(), login_url='login'), name='order_history'),
    path('all_clients/', views.all_clients, name='all_clients'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail'),
]