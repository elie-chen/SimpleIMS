from django import forms
from django.db import models
from django.urls import reverse
from basic.models import Currency, Customer, Product

CAT_CHOICES = [
    ('1', 'CAT1'),
    ('2', 'CAT2'),
    ('3', 'CAT3'),
]


ORDER_CHOICES = [
    ('N', u'尚未出货'),
    ('A', u'全部出货'),
    ('P', u'部分出货'),
    ('O', u'超额出货'),
]


class Order(models.Model):
    cat_id = models.CharField(max_length=2, choices=CAT_CHOICES, blank=False, verbose_name=u'Cat.')
    pi_no = models.CharField(max_length=16, verbose_name='PI #', blank=False, null=False, unique=True)
    po_no = models.CharField(max_length=16, verbose_name='PO #', blank=True)
    customer = models.ForeignKey(Customer, verbose_name=u'客户', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'},)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=True)
    is_urgency = models.BooleanField(verbose_name=u'是否为急单', default=False)
    status = models.CharField(max_length=1, choices=ORDER_CHOICES, default='N', verbose_name=u'状态')
    etd = models.DateField(blank=False, null=False, verbose_name=u'预定出货日期')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'订购时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('sale:order_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return 'Id:{}-PI #:{}- PO #:{}'.format(self.id, self.pi_no, self.po_no)

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = verbose_name
        permissions = (
            ('active_order', '可中止订单'),
        )


class OrderProduct(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    order = models.ForeignKey(Order, verbose_name=u'订单单头', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'商品', on_delete=models.DO_NOTHING,
                                limit_choices_to={'status': 'A'},)
    quantity = models.PositiveIntegerField(blank=False, verbose_name=u'订购数量')
    price = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'未税金额')
    tax = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'税金')
    tax_price = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'含税金额')
    subtotal = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'小计未税金额')
    tax_subtotal = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'小计含税金额')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', blank=False, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            order_products = OrderProduct.objects.filter(order=self.order)
            num = "{0:02d}".format(order_products.count() + 1)
            self.num = "{0:02d}".format(int(num))

        product = Product.objects.get(title=self.product)
        self.price = product.price
        self.tax = product.tax
        self.currency = product.currency
        self.tax_price = product.tax_price
        self.subtotal = product.price * self.quantity
        self.tax_subtotal = product.tax_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '订单单身'
        verbose_name_plural = verbose_name


class Ship(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'对应订单', on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, verbose_name=u'客户', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'})
    is_active = models.BooleanField(verbose_name=u'是否有效', default=False)
    is_delay = models.BooleanField(verbose_name=u'是否延迟', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'出货时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('sale:ship_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '出货单'
        verbose_name_plural = verbose_name
        permissions = (
            ('active_ship', '可中止出货单'),
        )


class ShipDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    ship = models.ForeignKey(Ship, verbose_name=u'出货单单头', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'出货商品', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False, verbose_name=u'出货数量')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            ship_detail = ShipDetail.objects.filter(ship=self.ship)
            num = "{0:02d}".format(ship_detail.count() + 1)
            self.num = "{0:02d}".format(int(num))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '出货单单身'
        verbose_name_plural = verbose_name

