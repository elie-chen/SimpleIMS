from django.db import models
from django.urls import reverse
from basic.models import Material, Product
from sale.models import Order


class Mcheck(models.Model):
    is_active = models.BooleanField(verbose_name=u'是否有效', default=False)
    description = models.CharField(max_length=256, verbose_name=u'申请原因')
    created = models.DateTimeField(auto_now=True, verbose_name=u'异动日期')
    create_user = models.ForeignKey('auth.User', verbose_name=u'异动人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('inventory:mcheck_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '原料库存异动申请单'
        verbose_name_plural = verbose_name


class McheckDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    mcheck = models.ForeignKey(Mcheck, verbose_name=u'原料库存异动申请单', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'},)
    quantity = models.IntegerField(verbose_name=u'异动数量',
                                   help_text=u'数量为正表示新增一个库存，数量为负表示减少一个库存')

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            mcheck_details = McheckDetail.objects.filter(mcheck=self.mcheck)
            num = "{0:02d}".format(mcheck_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '原料库存异动申请单单身'
        verbose_name_plural = verbose_name


class Pcheck(models.Model):
    is_active = models.BooleanField(verbose_name=u'是否有效', default=False)
    description = models.CharField(max_length=256, verbose_name=u'申请原因')
    created = models.DateTimeField(auto_now=True, verbose_name=u'异动日期')
    create_user = models.ForeignKey('auth.User', verbose_name=u'异动人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('inventory:pcheck_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '商品库存异动申请单'
        verbose_name_plural = verbose_name


class PcheckDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    pcheck = models.ForeignKey(Pcheck, verbose_name=u'商品库存异动申请单', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'商品', on_delete=models.PROTECT,
                                 limit_choices_to={'status': 'A'},)
    quantity = models.IntegerField(verbose_name=u'异动数量',
                                   help_text=u'数量为正表示新增一个库存，数量为负表示减少一个库存')

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            pcheck_details = PcheckDetail.objects.filter(pcheck=self.pcheck)
            num = "{0:02d}".format(pcheck_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '商品库存异动申请单单身'
        verbose_name_plural = verbose_name


PROCESS_CHOICES = (
    ('A', u'立单申请'),
    ('C', u'原料已出库'),
    ('R', u'商品已入库'),
)


class Process(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'对应订单', limit_choices_to={'status': 'N'},
                              help_text=u'仅显示"尚未出货"的订单', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=u'对应商品', limit_choices_to={'status': 'A'},
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=u'商品制程数量',
                                           help_text=u'请注意，存盘后，下方制程单单身的"原料数量"将会自动乘上此"商品制程数量"')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=PROCESS_CHOICES, default='A', verbose_name=u'制程状况')
    claimed = models.DateTimeField(null=True, verbose_name=u'原料出库日期')
    claim_user = models.ForeignKey('auth.User', related_name='claim_process', verbose_name=u'原料出库确认人员',
                                   null=True, on_delete=models.PROTECT)
    receipted = models.DateTimeField(null=True, verbose_name=u'商品入库时间')
    receipt_user = models.ForeignKey('auth.User', related_name='receipt_process', verbose_name=u'商品入库确认人员',
                                     null=True, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now=True, verbose_name=u'申请日期')
    create_user = models.ForeignKey('auth.User', verbose_name=u'申请人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('inventory:process_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '制程单'
        verbose_name_plural = verbose_name
        permissions = (
            ('check_process', '可确认制程单内商品与原料的出入库'),
        )


class ProcessDetail(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    process = models.ForeignKey(Process, verbose_name=u'制程单', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(verbose_name=u'数量')

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            process_details = ProcessDetail.objects.filter(process=self.process)
            num = "{0:02d}".format(process_details.count() + 1)
            self.num = "{0:02d}".format(int(num))

        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = '制程单单身'
        verbose_name_plural = verbose_name


MTRAIN_FORM_CHOICES = (
    ('ARRIVE', u'到货单'),
    ('MCHECK', u'原料库存异动申请单'),
    ('PROCESS', u'制程单'),
)


class Mtran(models.Model):
    material = models.ForeignKey(Material, verbose_name=u'原料', on_delete=models.CASCADE)
    source_form = models.CharField(max_length=12, choices=MTRAIN_FORM_CHOICES, blank=False,
                                   default='', verbose_name=u'来源单类别')
    source_id = models.PositiveIntegerField(default=0, verbose_name=u'来源单号')
    from_quantity = models.PositiveIntegerField(default=0, verbose_name=u'异动前数量')
    tran_quantity = models.IntegerField(default=0, verbose_name=u'异动数量')
    to_quantity = models.PositiveIntegerField(default=0, verbose_name=u'异动后数量')
    created = models.DateTimeField(auto_now=True, verbose_name=u'异动日期')
    create_user = models.ForeignKey('auth.User', verbose_name=u'异动人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('inventory:mtran_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '原料库存异动'
        verbose_name_plural = verbose_name


PTRAIN_FORM_CHOICES = (
    ('SHIP', u'出货单'),
    ('PCHECK', u'商品库存异动申请单'),
    ('PROCESS', u'制程单'),
)


class Ptran(models.Model):
    product = models.ForeignKey(Product, verbose_name=u'商品', on_delete=models.CASCADE)
    source_form = models.CharField(max_length=12, choices=PTRAIN_FORM_CHOICES, blank=False,
                                   default='', verbose_name=u'来源单类别')
    source_id = models.PositiveIntegerField(default=0, verbose_name=u'来源单号')
    from_quantity = models.PositiveIntegerField(default=0, verbose_name=u'异动前数量')
    tran_quantity = models.IntegerField(default=0, verbose_name=u'异动数量')
    to_quantity = models.PositiveIntegerField(default=0, verbose_name=u'异动后数量')
    created = models.DateTimeField(auto_now=True, verbose_name=u'异动日期')
    create_user = models.ForeignKey('auth.User', verbose_name=u'异动人员', on_delete=models.PROTECT)

    def get_absolute_url(self):
        return reverse('inventory:ptran_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = '商品库存异动'
        verbose_name_plural = verbose_name
