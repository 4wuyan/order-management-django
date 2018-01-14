from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Client, ClientPayment, Order, OrderItem
from django.views import generic
from django.http import HttpResponse, HttpResponseNotFound

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required(login_url='/orders/login')
def profile(request):
    if request.user.groups.filter(name='view_all'):
        return render(request, 'orders/profile_view_all.html')
    client = get_object_or_404(Client, name=request.user.username)
    pay_amount = 0
    buy_amount = 0
    try:
        payments = get_list_or_404(ClientPayment, client=client)
        for payment in payments:
            pay_amount += payment.amount_CNY
    except:
        pass
    try:
        orders = get_list_or_404(Order, client=client)
        for order in orders:
            order.find_total_price()
            buy_amount += order.final_CNY
    except:
        pass
    context = {'client':client, 'pay_amount':pay_amount, 'buy_amount':buy_amount, 'balance':pay_amount - buy_amount}
    return render(request, 'orders/profile.html', context)

@user_passes_test(lambda user : user.groups.filter(name='view_all').exists(), login_url='/orders/login')
def all_payment_history(request):
    try:
        payments = get_list_or_404(ClientPayment)
        payments.reverse()
    except:
        payments = None
    return render(request, 'orders/all_payment_history.html', {'payment_list':payments})

@user_passes_test(lambda user : user.groups.filter(name='view_all').exists(), login_url='/orders/login')
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
        try:
            client = get_object_or_404(Client, name=self.request.user.username)
            payments = get_list_or_404(ClientPayment, client=client)
            payments.reverse()
            return payments
        except:
            return None

class OrderHistoryView(generic.ListView):
    template_name = 'orders/order_history.html'
    context_object_name = 'order_list'
    def get_queryset(self):
        try:
            client = get_object_or_404(Client, name=self.request.user.username)
            orders = get_list_or_404(Order, client=client)
            orders.reverse()
            for o in orders:
                o.find_total_price()
            return orders
        except:
            return None

@login_required(login_url='/orders/login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.user.username == order.client.name or request.user.groups.filter(name='view_all').exists():
        order.find_total_price()
        item_list = get_list_or_404(OrderItem, order=order)
        context = {'order':order, 'item_list':item_list}
        return render(request, 'orders/order_detail.html', context)
    else:
        return render(request, 'orders/order_detail_denied.html')