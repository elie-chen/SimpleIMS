from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename

import datetime
from .models import Order, OrderProduct, Ship, ShipDetail
from finance.models import Receivable, ReceivableDetail
from inventory.models import Ptran


"""
订单单身检查
1.最少要有一个单身
2.商品不可重复
3.商品数量是否大于0
"""
class OrderProductCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        product_list = []
        for form in self.forms:
            if form.cleaned_data:
                count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity <= 0:
                    raise forms.ValidationError(u'订单中商品数量不得为0或是负数。')

                product_id = form.cleaned_data.get('product')
                if product_id in product_list:
                    raise forms.ValidationError(u'订单中商品不得重复。')
                else:
                    product_list.append(product_id)

        if count < 1:
            raise forms.ValidationError(u'您最少必须输入一笔订单单身。')


class OrderProductInline(admin.TabularInline):
    formset = OrderProductCheckInlineFormset
    model = OrderProduct
    fields = ['product', 'quantity', 'description']
    raw_id_fields = ['product']
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'cat_id', 'pi_no', 'po_no', 'customer', 'is_urgency', 'status',
                    'etd', 'created', 'create_user']
    fields = ['cat_id', 'po_no', 'customer', 'is_urgency', 'etd']
    list_filter = ['is_urgency', 'status']
    actions = ['make_actived']
    inlines = [OrderProductInline]
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user

            """
            pi_no的格式是R201901121
            R:开头
            201901:2019年1月
            121:三码流水码
            """
            pattern = 'R' + datetime.datetime.now().strftime("%Y%m")
            orders = Order.objects.filter(pi_no__startswith=pattern)
            obj.pi_no = pattern + "{0:03d}".format(orders.count() + 1)
        super().save_model(request, obj, form, change)

    def make_actived(self, request, queryset):
        rows = queryset.update(is_active=False)
        if rows > 0:
            self.message_user(request, u'已完成终止订单动作')
    make_actived.allowed_permissions = ('active',)
    make_actived.short_description = u'终止订单'

    def has_active_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('active', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Order, OrderAdmin)


"""
出货单单身检查
1.最少要有一个单身
2.商品库存是否足够
3.出货数量是否至少一笔大于0
4.出货数量不得是负数
4.单身商品不得重复
"""
class ShipDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        detail_count = 0
        detail_amount = 0

        product_list = []
        for form in self.forms:
            if form.cleaned_data:
                detail_count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity < 0:
                    raise forms.ValidationError(u'出货单中商品数量不得是负数。')
                elif quantity > 0:
                    detail_amount += 1

                product = form.cleaned_data.get('product')
                quantity = int(form.cleaned_data.get('quantity'))
                if product.stock < quantity:
                    raise forms.ValidationError(u"商品[{}-{}]库存 {}，无法满足此次出货量 {}，"
                                                u"请先填写制程单增加商品库存。".format(product.id, product.title,
                                                                         product.stock, quantity))

                if product.id in product_list:
                    raise forms.ValidationError(u"单身商品[{}-{}]已重复，"
                                                u"请重新填写出货单。".format(product.id, product.title))
                else:
                    product_list.append(product.id)
        if detail_count < 1:
            raise forms.ValidationError(u'您必须最少输入一笔订单单身')
        if detail_amount < 1:
            raise forms.ValidationError(u'您必须最少一笔出货单单身数量大于0')


class ShipDetailInline(admin.TabularInline):
    formset = ShipDetailCheckInlineFormset
    model = ShipDetail
    fields = ['product', 'quantity', 'description']
    raw_id_fields = ['product']
    extra = 0


"""
出货时的相关动作如下：
1.对于每个出货单单身而言
   i.新增 商品库存异动(Ptran)
  ii.如果出货数量>0时则新增 应收帐款单身(ReceivableDetail)
 iii.减少 商品库存量(product.stock)
2.对于整个出货单而言
   i.将出货单的 状态修改为有效出货(is_active=True) 检查出货日期是否有延迟(is_delay)
  ii.如果出货数量>0时则新增一笔 应收帐款(Receivable)
 iii.检查订单数量是否满足，决定订单"状态"，('A', '全部出货'),('P', '部分出货')
"""
class ShipAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'customer', 'is_active', 'is_delay', 'created', 'create_user']
    fields = ['order']
    actions = ['make_actived']
    inlines = [ShipDetailInline]
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'order':
            kwargs['queryset'] = Order.objects.filter(is_active=True).exclude(status='A')
        return super(ShipAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
            order = obj.order
            obj.customer = order.customer
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        ship = form.save(commit=False)

        #新增应收帐款单头
        receivable = Receivable()
        receivable.ship = ship
        receivable.customer = ship.customer
        #应收日期=出货日期 + 帐期
        receivable.receivabled = datetime.datetime.now().date() + datetime.timedelta(days=ship.customer.period.period)
        receivable.create_user = ship.create_user
        receivable.save()

        ship_details = ShipDetail.objects.filter(ship=ship)
        for ship_detail in ship_details:
            #新增商品库存异动
            product = ship_detail.product
            stock = product.stock
            tran_quantity = ship_detail.quantity

            ptran = Ptran()
            ptran.product = product
            ptran.source_form = 'SHIP'
            ptran.source_id = ship.id
            ptran.from_quantity = stock
            ptran.tran_quantity = 0 - tran_quantity
            ptran.to_quantity = stock - tran_quantity
            ptran.create_user = request.user
            ptran.save()

            #新增应收帐款单身
            receivable_detail = ReceivableDetail()
            receivable_detail.receivable = receivable
            receivable_detail.product = product
            receivable_detail.amount = product.tax_price * tran_quantity
            receivable_detail.currency = product.currency
            receivable_detail.save()

            #减少商品库存量
            product.stock = stock - tran_quantity
            product.save()

        order = form.cleaned_data.get('order')
        #修改出货单状态
        ship.is_active = True
        today = datetime.datetime.now().date()
        if today > order.etd:
            ship.is_delay = True
        ship.save()

        #决定对应订单状态('A', '全部出货'),('P', '部分出货')，('O', '超额出货')如果有一个订单单身数量没有全部出完的话，则状态为P
        order_products = OrderProduct.objects.filter(order=order)
        ships = Ship.objects.filter(order=order)
        status = 'A'
        for order_product in order_products:
            product = order_product.product
            shipped_quantity = 0
            for ship in ships.all():
                ship_details = ShipDetail.objects.filter(product=product, ship=ship)
                if ship_details.all().count() > 0:
                    for ship_detail in ship_details.all():
                        shipped_quantity += ship_detail.quantity

            if shipped_quantity < order_product.quantity:
                status = 'P'
            else:
                if shipped_quantity > order_product.quantity:
                    #如果有商品是部分出货P，就算是有超额出货也还是算成P
                    if status is 'P':
                        status = 'P'
                    else:
                        status = 'O'

        order.status = status
        order.save()

        #如果没有发生错误则修改应收帐款状态
        receivable.is_active = True
        receivable.save()

    def make_actived(self, request, queryset):
        rows = queryset.update(is_active=False)
        if rows > 0:
            self.message_user(request, u'已完成终止出货单动作')
    make_actived.allowed_permissions = ('active',)
    make_actived.short_description = u'终止出货单'

    def has_active_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('active', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Ship, ShipAdmin)

