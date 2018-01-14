from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='orders/login.html'), name='login'),
    path('profile/', views.profile, name='profile'),
    path('payment_history/', login_required(views.PaymentHistoryView.as_view()), name='payment_history'),
    path('order_history/', login_required(views.OrderHistoryView.as_view()), name='order_history'),
    path('all_payment_history/', views.all_payment_history, name='all_payment_history'),
    path('all_order_history/', views.all_order_history, name='all_order_history'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail'),
]