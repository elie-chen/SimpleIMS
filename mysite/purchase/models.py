from django.db import models
from django.urls import reverse
from basic.models import Currency, Material, Supplier
from sale.models import Order


CORRESPOND_CHOICES = [
    ('1', u'有对应订单'),
    ('0', u'无对应订单'),
]


PROCUREMENT_CHOICES = [
    ('N', u'尚未到货'),
    ('A', u'全部到货'),
    ('P', u'部分到货'),
    ('O', u'超额到货'),
]


class Procurement(models.Model):
    is_correspond = models.CharField(max_length=1, choices=CORRESPOND_CHOICES,
                                     verbose_name=u'是否有对应订单')
    order = models.ForeignKey(Order, verbose_name=u'对应订单', on_delete=models.PROTECT,
                              limit_choices_to={'status': 'N', 'is_active': True},
                              help_text=u'仅找尚未出货的订单', blank=True, null=True)
    supplier = models.ForeignKey(Supplier, verbose_name=u'供货商', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'},)
    is_active = models.BooleanField(verbose_name=u'是否有效', default=True)
    status = models.CharField(max_length=1, choices=PROCUREMENT_CHOICES, default='N', verbose_name=u'状态')
    etd = models.DateField(blank=False, null=False, verbose_name=u'预定到货日期')
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'采购时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('purchase:procurement_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '采购单'
        verbose_name_plural = verbose_name
        permissions = (
            ('active_procurement', '可中止采购单'),
        )


class ProcurementMaterial(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    procurement = models.ForeignKey(Procurement, verbose_name=u'采购单单头', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.DO_NOTHING,
                                 limit_choices_to={'status': 'A'},)
    quantity = models.PositiveIntegerField(blank=False, verbose_name=u'采购数量')
    price = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'未税金额')
    tax = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'税金')
    tax_price = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'含税金额')
    subtotal = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'小计未税金额')
    tax_subtotal = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'小计含税金额')
    tax_pay = models.DecimalField(max_digits=16, decimal_places=4, blank=False, default=0, verbose_name=u'已付含税金额')
    currency = models.ForeignKey(Currency, verbose_name=u'币别', blank=False, on_delete=models.DO_NOTHING)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            procurement_materials = ProcurementMaterial.objects.filter(procurement=self.procurement)
            num = "{0:02d}".format(procurement_materials.count() + 1)
            self.num = "{0:02d}".format(int(num))

        material = Material.objects.get(title=self.material)
        self.price = material.price
        self.tax = material.tax
        self.currency = material.currency
        self.tax_price = material.tax_price
        self.subtotal = material.price * self.quantity
        self.tax_subtotal = material.tax_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '采购单单身'
        verbose_name_plural = verbose_name


class Arrive(models.Model):
    procurement = models.ForeignKey(Procurement, verbose_name=u'对应采购单',
                                    help_text=u'仅显示"有效"且非"全部到货"的采购单', on_delete=models.PROTECT)
    supplier = models.ForeignKey(Supplier, verbose_name=u'供货商', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'})
    is_active = models.BooleanField(verbose_name=u'是否有效', default=True)
    is_delay = models.BooleanField(verbose_name=u'是否延迟', default=False)
    created = models.DateTimeField(auto_now_add=True, verbose_name=u'到货时间')
    create_user = models.ForeignKey('auth.User', verbose_name=u'建立人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('sale:ship_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '到货单'
        verbose_name_plural = verbose_name
        permissions = (
            ('active_arrive', '可中止到货单'),
        )


class ArriveDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    arrive = models.ForeignKey(Arrive, verbose_name=u'到货单单头', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'到货原料', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(blank=False, verbose_name=u'到货数量')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            arrive_detail = ArriveDetail.objects.filter(arrive=self.arrive)
            num = "{0:02d}".format(arrive_detail.count() + 1)
            self.num = "{0:02d}".format(int(num))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '到货单单身'
        verbose_name_plural = verbose_name

