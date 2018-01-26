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
        return render(request, 'orders/profile_manager.html')
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

class PaymentHistoryView(generic.ListView):
    template_name = 'orders/payment_history.html'
    context_object_name = 'payment_list'
    def get_queryset(self):
        client_name = self.kwargs['client_name']
        if not can_view(self.request.user, client_name):
            raise PermissionDenied
        try:
            if client_name == 'all':
                payments = get_list_or_404(ClientPayment)
            else:
                client = get_object_or_404(Client, name=client_name)
                payments = get_list_or_404(ClientPayment, client=client)
            payments.reverse()
            return payments
        except:
            return None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_name'] = self.kwargs['client_name']
        context['is_manager'] = is_manager(self.request.user)
        return context


class OrderHistoryView(generic.ListView):
    template_name = 'orders/order_history.html'
    context_object_name = 'order_list'
    def get_queryset(self):
        client_name = self.kwargs['client_name']
        if not can_view(self.request.user, client_name):
            raise PermissionDenied
        try:
            if client_name == 'all':
                orders = get_list_or_404(Order)
            else:
                client = get_object_or_404(Client, name=client_name)
                orders = get_list_or_404(Order, client=client)
            orders.reverse()
            for o in orders:
                o.set_all_prices()
            return orders
        except:
            return None
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_name'] = self.kwargs['client_name']
        context['is_manager'] = is_manager(self.request.user)
        return context

@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    _is_manager = is_manager(request.user)
    if request.user.username == order.client.name or _is_manager:
        order.set_all_prices()
        item_list = get_list_or_404(OrderItem, order=order)
        context = {'order':order, 'item_list':item_list, 'is_manager':_is_manager}
        return render(request, 'orders/order_detail.html', context)
    else:
        raise PermissionDenied

