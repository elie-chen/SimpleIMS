from django.db import models
from django.urls import reverse


class Currency(models.Model):
    id = models.CharField(max_length=3, primary_key=True, verbose_name=u'币别代号')
    title = models.CharField(max_length=8, blank=False, verbose_name=u'币别')
    rate = models.DecimalField(max_digits=16, decimal_places=4, blank=False, verbose_name=u'汇率')

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = '币别'
        verbose_name_plural = verbose_name


class Period(models.Model):
    title = models.CharField(max_length=32, blank=False, verbose_name=u'帐期名称')
    period = models.PositiveIntegerField(blank=False, verbose_name=u'天数', help_text=u'天数为整数')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '帐期'
        verbose_name_plural = verbose_name


STATUS_CHOICES = (
    ('W', u'等待审核'),
    ('A', u'已审核'),
    ('S', u'停止使用'),
)


class Supplier(models.Model):
    title = models.CharField(max_length=128, unique=True, blank=False, verbose_name=u'名称')
    contacter = models.CharField(max_length=32, verbose_name=u'联络人', blank=True)
    period = models.ForeignKey(Period, verbose_name=u'帐期', on_delete=models.PROTECT)
    landline = models.CharField(max_length=16, verbose_name=u'联络市话', blank=True)
    mobile = models.CharField(max_length=16, verbose_name=u'联络手机号', help_text='ex:12345678901',blank=True)
    wechat_account = models.CharField(max_length=16, verbose_name=u'联络微信账号', blank=True)
    email = models.EmailField(verbose_name=u'联络email', blank=True)
    address = models.CharField(max_length=256, verbose_name=u'联络地址', blank=True)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')

    def get_absolute_url(self):
        return reverse('basic:supplier_detail', args=[self.id])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '供货商'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_supplier', '可审核供货商'),
            ('stop_supplier', '可终止供货商'),
        )


class Customer(models.Model):
    title = models.CharField(max_length=128, unique=True, blank=False, verbose_name=u'名称')
    contacter = models.CharField(max_length=32, verbose_name=u'联络人', blank=True)
    period = models.ForeignKey(Period, verbose_name=u'帐期', on_delete=models.PROTECT)
    landline = models.CharField(max_length=16, verbose_name=u'联络市话', blank=True)
    mobile = models.CharField(max_length=16, verbose_name=u'联络手机号', help_text='ex:12345678901', blank=True)
    wechat_account = models.CharField(max_length=16, verbose_name=u'联络微信账号', blank=True)
    email = models.EmailField(verbose_name=u'联络email', blank=True)
    address = models.CharField(max_length=256, verbose_name=u'联络地址', blank=True)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')

    def get_absolute_url(self):
        return reverse('basic:customer_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_customer', '可审核客户'),
            ('stop_customer', '可终止客户'),
        )


class Category(models.Model):
    title = models.CharField(max_length=64, unique=True, blank=False, verbose_name=u'Part Number')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')

    def get_absolute_url(self):
        return reverse('basic:category_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '原料种类'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_category', '可审核原料种类'),
            ('stop_category', '可终止原料种类'),
        )


class Part(models.Model):
    title = models.CharField(max_length=64, unique=True, blank=False, verbose_name=u'Part Number')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')

    def get_absolute_url(self):
        return reverse('basic:part_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '商品Part'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_part', '可审核商品Part'),
            ('stop_part', '可终止商品Part'),
        )


class Size(models.Model):
    title = models.CharField(max_length=64, unique=True, blank=False, verbose_name=u'size')
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')

    def get_absolute_url(self):
        return reverse('basic:size_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '商品Size'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_size', '可审核商品Size'),
            ('stop_size', '可终止商品Size'),
        )


class Material(models.Model):
    title = models.CharField(max_length=64, unique=True, blank=False, verbose_name=u'料号')
    image_sub = models.CharField(max_length=64, verbose_name=u'图文件在google共享文件夹的位置', blank=False, null=False)
    supplier = models.ForeignKey(Supplier, verbose_name=u'供货商', on_delete=models.PROTECT)
    category = models.ForeignKey(Category, verbose_name=u'种类', on_delete=models.PROTECT, limit_choices_to={'status': 'A'},)
    price = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'未税价', null=False, blank=False)
    tax = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'税金', null=False, blank=False)
    tax_price = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'含税价', null=False, blank=False)
    currency = models.ForeignKey(Currency, verbose_name=u'报价币别', blank=False, null=False, on_delete=models.PROTECT)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')
    stock = models.PositiveIntegerField(default=0, verbose_name=u'库存数量')

    def get_absolute_url(self):
        return reverse('basic:material_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '原料'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_material', '可审核原料'),
            ('stop_material', '可终止原料'),
        )


class Product(models.Model):
    title = models.CharField(max_length=64, unique=True, blank=False, verbose_name='Model Name')
    part = models.ForeignKey(Part, verbose_name='Part Number', null=True, blank=True,
                             on_delete=models.PROTECT, limit_choices_to={'status': 'A'},)
    size = models.ForeignKey(Size, verbose_name='size', on_delete=models.PROTECT, limit_choices_to={'status': 'A'},)
    image_sub = models.CharField(max_length=64, verbose_name=u'图文件在google共享文件夹的位置', blank=False, null=False)
    price = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'未税价', null=False, blank=False)
    tax = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'税金', null=False, blank=False)
    tax_price = models.DecimalField(max_digits=16, decimal_places=4, verbose_name=u'含税价', null=False, blank=False)
    currency = models.ForeignKey(Currency, verbose_name=u'报价币别', blank=False, null=False, on_delete=models.PROTECT)
    description = models.CharField(max_length=256, verbose_name=u'描述', blank=True)
    combines = models.ManyToManyField(Material, through='Bom')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name=u'状态')
    stock = models.PositiveIntegerField(default=0, verbose_name=u'库存数量')

    def get_absolute_url(self):
        return reverse('basic:product_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = u'商品'
        verbose_name_plural = verbose_name
        permissions = (
            ('audit_product', '可审核商品'),
            ('stop_product', '可终止商品'),
        )


class Bom(models.Model):
    num = models.CharField(max_length=2, default='', verbose_name=u'单身项次')
    product = models.ForeignKey(Product, verbose_name='商品', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, verbose_name='原料', on_delete=models.PROTECT, limit_choices_to={'status': 'A'},)
    quantity = models.PositiveIntegerField(default=1, verbose_name=u'组成数量')

    def save(self, *args, **kwargs):
        if self.num == '':
            #项次的格式是01,02...
            boms = Bom.objects.filter(product=self.product)
            num = "{0:02d}".format(boms.count() + 1)
            self.num = "{0:02d}".format(int(num))
        super().save(*args, **kwargs)

    def __str__(self):
        return '{}'.format(self.num)

    class Meta:
        verbose_name = 'BOM表'
        verbose_name_plural = verbose_name

