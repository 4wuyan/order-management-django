from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

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
                order.set_all_prices()
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
    actual_deduction_CNY = models.DecimalField('实扣', max_digits=10, decimal_places=2, blank=True, null=True, db_column='actual_deduction_CNY')
    comment = models.CharField(max_length=200, blank=True, db_column='comment')
    class Meta:
        db_table = 'Order'
    def __str__(self):
        answer = str(self.client.name) + ' ' + str(self.date) + ' ' + str(self.exchange_rate) + ' ' + str(self.actual_deduction_CNY)
        if self.comment:
            answer += '\n' + self.comment
        return answer

    def set_all_prices(self):
        items = OrderItem.objects.filter(order=self)
        total = Decimal('0')
        for item in items:
            total = total + item.price_AUD * item.item_number
        self.total_price_AUD = total
        self.total_price_CNY = round(total * Decimal(str(self.exchange_rate)), 2)
        self.final_CNY = self.actual_deduction_CNY if self.actual_deduction_CNY else self.total_price_CNY
    def get_total_price_CNY(self):
        if not hasattr(self, 'total_price_CNY'):
            self.set_all_prices()
        return self.total_price_CNY
    get_total_price_CNY.short_description = '约合'
    def get_item_list(self):
        items = OrderItem.objects.filter(order=self)
        item_number_dict = {}
        for item in items:
            name = item.item_name
            num = item.item_number
            if name not in item_number_dict:
                item_number_dict[name] = 0
            item_number_dict[name] += num
        string_list = []
        for name in item_number_dict:
            item_string = name
            num = item_number_dict[name]
            if num > 1:
                item_string += ' x' + str(num)
            string_list.append(item_string)
        return '，'.join(string_list)
    get_item_list.short_description = '清单'

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