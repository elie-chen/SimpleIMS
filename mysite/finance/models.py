from django.db import models
from django.urls import reverse
from basic.models import Currency, Customer, Material, Product, Supplier
from sale.models import Ship
from purchase.models import Arrive

RECEIVABLE_CHOICES = [
    ('N', u'尚未收款'),
    ('A', u'全部收款'),
    ('P', u'部分收款'),
    ('O', u'超额收款'),
]

class Receivable(models.Model):
    ship = models.ForeignKey(Ship, verbose_name=u'对应出货单', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name=u'客户', on_delete=models.PROTECT)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=False)
    status = models.CharField(max_length=1, choices=RECEIVABLE_CHOICES, default='N', verbose_name=u'状态')
    receivabled = models.DateField(verbose_name=u'应收日期')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'建立时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('finance:receivable_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '应收帐款'
        verbose_name_plural = verbose_name


class ReceivableDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    receivable = models.ForeignKey(Receivable, verbose_name=u'应收帐款单头', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'商品', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'金额')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            receivable_details = ReceivableDetail.objects.filter(receivable=self.receivable)
            num = "{0:02d}".format(receivable_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '应收帐款单身'
        verbose_name_plural = verbose_name


class Receive(models.Model):
    invoice_no = models.CharField(max_length=12, blank=False, null=False,
                                  verbose_name=u'发票号码', help_text=u'收款时必须登打发票号码')
    receivable = models.ForeignKey(Receivable, verbose_name=u'对应应收帐款',
                                   help_text=u'仅显示"有效"且非"全部收款"的应收帐款', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name=u'客户', on_delete=models.PROTECT)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=True)
    is_delay = models.BooleanField(verbose_name=u'是否延迟', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'收款时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('finance:receive_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '收款单'
        verbose_name_plural = verbose_name


class ReceiveDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    receive = models.ForeignKey(Receive, verbose_name=u'收款单单头', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'商品', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'金额')
    discount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, null=False, verbose_name=u'折扣')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', blank=False, null=False, on_delete=models.PROTECT)
    rate = models.DecimalField(max_digits=16, decimal_places=4, blank=False, null=False, verbose_name=u'汇率')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            receive_details = ReceiveDetail.objects.filter(receive=self.receive)
            num = "{0:02d}".format(receive_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '收款单单身'
        verbose_name_plural = verbose_name


DUE_CHOICES = [
    ('N', u'尚未付款'),
    ('A', u'全部付款'),
    ('P', u'部分付款'),
    ('O', u'超额付款'),
]

class Due(models.Model):
    arrive = models.ForeignKey(Arrive, verbose_name=u'对应到货单', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, verbose_name=u'供货商', on_delete=models.PROTECT)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=False)
    status = models.CharField(max_length=1, choices=DUE_CHOICES, default='N', verbose_name=u'状态')
    dued = models.DateField(verbose_name=u'应付日期')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'建立时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('finance:due_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '应付帐款'
        verbose_name_plural = verbose_name


class DueDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    due = models.ForeignKey(Due, verbose_name=u'应付帐款单头', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'金额')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            due_details = DueDetail.objects.filter(due=self.due)
            num = "{0:02d}".format(due_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '应付帐款单身'
        verbose_name_plural = verbose_name


class Pay(models.Model):
    invoice_no = models.CharField(max_length=12, blank=False, null=False,
                                  verbose_name=u'发票号码', help_text=u'付款时必须输入供货商提供的发票号码')
    due = models.ForeignKey(Due, verbose_name=u'对应应付帐款',
                            help_text=u'仅显示"有效"且非"全部付款"的应付帐款', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, verbose_name=u'供货商', on_delete=models.PROTECT)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=True)
    is_delay = models.BooleanField(verbose_name=u'是否延迟', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'付款时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('finance:pay_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '付款单'
        verbose_name_plural = verbose_name


class PayDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    pay = models.ForeignKey(Pay, verbose_name=u'付款单单头', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'金额')
    discount = models.DecimalField(max_digits=16, decimal_places=4, blank=False, null=False, verbose_name=u'折扣')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', blank=False, null=False, on_delete=models.PROTECT)
    rate = models.DecimalField(max_digits=16, decimal_places=4, blank=False, null=False, verbose_name=u'汇率')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            pay_details = PayDetail.objects.filter(pay=self.pay)
            num = "{0:02d}".format(pay_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '付款单单身'
        verbose_name_plural = verbose_name

