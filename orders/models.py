from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=20, primary_key=True, db_column='name')
    comment = models.CharField(max_length=200, blank=True, db_column='comment')
    #user = models.OneToOneField(User, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'Client'

    def __str__(self):
        return self.name + ' ' + self.comment

    def get_balance(self):
        pay_amount = 0
        buy_amount = 0
        try:
            payments = ClientPayment.objects.filter(client=self)
            for payment in payments:
                pay_amount += payment.amount_CNY
        except:
            pass
        try:
            orders = Order.objects.filter(client=self)
            for order in orders:
                order.find_total_price()
                buy_amount += order.final_CNY
        except:
            pass
        self.balance = pay_amount - buy_amount
        self.pay_amount = pay_amount
        self.buy_amount = buy_amount
        return self.balance

class ClientPayment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client')
    date = models.DateField(db_column='date')
    amount_CNY = models.DecimalField(max_digits=10, decimal_places=2, db_column='amount_CNY')
    comment = models.CharField(max_length=200, blank=True, db_column='comment')
    class Meta:
        db_table = 'ClientPayment'
    def __str__(self):
        answer = str(self.client.name) + ' ' + str(self.date) + ' 付 ￥' + str(self.amount_CNY)
        if self.comment:
            answer += '\n' + self.comment
        return answer

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, db_column='client')
    date = models.DateField(db_column='date')
    exchange_rate = models.FloatField(blank=True, null=True, db_column='exchange_rate')
    actual_deduction_CNY = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, db_column='actual_deduction_CNY')
    comment = models.CharField(max_length=200, blank=True, db_column='comment')
    class Meta:
        db_table = 'Order'
    def __str__(self):
        answer = str(self.client.name) + ' ' + str(self.date) + ' ' + str(self.exchange_rate) + ' ' + str(self.actual_deduction_CNY)
        if self.comment:
            answer += '\n' + self.comment
        return answer
    def find_total_price(self):
        items = OrderItem.objects.filter(order=self)
        from decimal import Decimal
        total = Decimal('0')
        for item in items:
            total = total + item.price_AUD * item.item_number
        self.total_price_AUD = total
        self.total_price_CNY = round(total * Decimal(str(self.exchange_rate)), 2)
        self.final_CNY = self.actual_deduction_CNY if self.actual_deduction_CNY else self.total_price_CNY

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_column='order')
    item_name = models.CharField(max_length=200, db_column='item_name')
    price_AUD = models.DecimalField(max_digits=10, decimal_places=2, db_column='price_AUD')
    item_number = models.IntegerField(default=1, db_column='item_number')
    comment = models.CharField(max_length=200, blank=True, db_column='comment')
    class Meta:
        db_table = 'OrderItem'
    def __str__(self):
        answer = str(self.order.id) + ' ' + str(self.item_name) + ' ' + str(self.price_AUD) +' ' + str(self.item_number)
        if self.comment:
            answer += '\n' + self.comment
        return answer