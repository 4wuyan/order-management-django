from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Client, ClientPayment, Order, OrderItem
from django.views import generic
from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import PermissionDenied

def can_view(user, client_name):
    if is_manager(user):
        return True
    elif client_name == user.username:
        return True
    return False
def is_manager(user):
    return user.groups.filter(name='view_all').exists()

@login_required(login_url='login')
def index(request):
    if is_manager(request.user):
        return render(request, 'orders/profile_view_all.html')
    return redirect(profile, client_name = request.user.username)

@login_required(login_url='login')
def profile(request, client_name):
    if not can_view(request.user, client_name):
        raise PermissionDenied
    client = get_object_or_404(Client, name=client_name)
    client.get_balance()
    context = {'client':client}
    return render(request, 'orders/profile.html', context)

@user_passes_test(is_manager, login_url='login')
def all_clients(request):
    try:
        client_list = get_list_or_404(Client)
    except:
        client_list = None
    return render(request, 'orders/all_clients.html', {'client_list':client_list})

@user_passes_test(is_manager, login_url='login')
def all_payment_history(request):
    try:
        payments = get_list_or_404(ClientPayment)
        payments.reverse()
    except:
        payments = None
    return render(request, 'orders/all_payment_history.html', {'payment_list':payments})

@user_passes_test(is_manager, login_url='login')
def all_order_history(request):
    try:
        orders = get_list_or_404(Order)
        orders.reverse()
        for o in orders:
            o.find_total_price()
    except:
        orders = None
    return render(request, 'orders/all_order_history.html', {'order_list':orders})

class PaymentHistoryView(generic.ListView):
    template_name = 'orders/payment_history.html'
    context_object_name = 'payment_list'
    def get_queryset(self):
        client_name = self.kwargs['client_name']
        if not can_view(self.request.user, client_name):
            raise PermissionDenied
        try:
            client = get_object_or_404(Client, name=client_name)
            payments = get_list_or_404(ClientPayment, client=client)
            payments.reverse()
            return payments
        except:
            return None

class OrderHistoryView(generic.ListView):
    template_name = 'orders/order_history.html'
    context_object_name = 'order_list'
    def get_queryset(self):
        client_name = self.kwargs['client_name']
        if not can_view(self.request.user, client_name):
            raise PermissionDenied
        try:
            client = get_object_or_404(Client, name=client_name)
            orders = get_list_or_404(Order, client=client)
            orders.reverse()
            for o in orders:
                o.find_total_price()
            return orders
        except:
            return None

@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.user.username == order.client.name or is_manager(request.user):
        order.find_total_price()
        item_list = get_list_or_404(OrderItem, order=order)
        context = {'order':order, 'item_list':item_list}
        return render(request, 'orders/order_detail.html', context)
    else:
        raise PermissionDenied

