from django import forms
from django.contrib import admin
from .models import Due, DueDetail, Pay, PayDetail, Receivable, ReceivableDetail, Receive, ReceiveDetail
from purchase.models import ProcurementMaterial
from sale.models import OrderProduct
import datetime


class ReceivableDetailInline(admin.TabularInline):
    model = ReceivableDetail
    fields = ['product', 'amount', 'currency']
    extra = 0


class ReceivableAdmin(admin.ModelAdmin):
    list_display = ['id', 'ship', 'customer', 'is_active', 'status', 'receivabled', 'created', 'create_user']
    fields = ['ship', 'customer', 'is_active', 'status', 'create_user']
    inlines = [ReceivableDetailInline]
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'receivabled'


admin.site.register(Receivable, ReceivableAdmin)


"""
收款单单身检查
1.最少要有一个单身
2.收款金额是否至少一笔大于0
3.收款金额不得是负数
4.单身商品不得重复
"""
class ReceiveDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        detail_count = 0
        detail_amount = 0

        product_list = []
        for form in self.forms:
            if form.cleaned_data:
                detail_count += 1

                amount = form.cleaned_data.get('amount')
                if amount < 0:
                    raise forms.ValidationError(u'收款单中收款金额不得为负数。')
                elif amount > 0:
                    detail_amount += 1

                product = form.cleaned_data.get('product')
                if product.id in product_list:
                    raise forms.ValidationError(u"单身商品[{}-{}]收款已重复，"
                                                u"请重新填写收款单。".format(product.id, product.title))
                else:
                    product_list.append(product.id)

        if detail_count < 1:
            raise forms.ValidationError(u'您必须最少输入一笔收款单单身')
        if detail_amount < 1:
            raise forms.ValidationError(u'您必须最少一笔收款单单身金额大于0')


class ReceiveDetailInline(admin.TabularInline):
    formset = ReceiveDetailCheckInlineFormset
    model = ReceiveDetail
    fields = ['product', 'amount', 'discount', 'currency', 'rate', 'description']
    raw_id_fields = ['product', 'currency']
    extra = 0


"""
收款时的相关动作如下：
1.检查收款日期是否有延迟(is_delay)
2.检查应收帐款金额是否满足，决定应收帐款"状态"，('A', u'全部收款'),('P', u'部分收款'),('O', '超额收款')
3.更新订单单身的已收含税金额(tax_receive)
"""
class ReceiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_no', 'receivable', 'customer', 'is_active', 'created', 'create_user']
    fields = ['receivable', 'invoice_no']
    inlines = [ReceiveDetailInline]
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'receivable':
            kwargs['queryset'] = Receivable.objects.filter(is_active=True).exclude(status='A')
        return super(ReceiveAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
            receivable = obj.receivable
            obj.customer = receivable.customer
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        #决定对应应收帐款状态('A', '全部收款'),('P', '部分收款')，('O', '超额收款')
        # 如果有一个应收帐款单身金额没有全部出完的话，则状态为P
        receivable = form.cleaned_data.get('receivable')
        ship = receivable.ship
        order = ship.order
        receivable_details = ReceivableDetail.objects.filter(receivable=receivable)
        receives = Receive.objects.filter(receivable=receivable)
        status = 'A'
        for receivable_detail in receivable_details:
            product = receivable_detail.product
            order_products = OrderProduct.objects.filter(order=order, product=product)
            if order_products.count() > 0:
                order_product = order_products[0]
                received_amount = 0
                for receive in receives.all():
                    receive_details = ReceiveDetail.objects.filter(product=product, receive=receive)
                    if receive_details.all().count() > 0:
                        for receive_detail in receive_details.all():
                            received_amount += receive_detail.amount + receive_detail.discount

            if received_amount < receivable_detail.amount:
                status = 'P'
            else:
                if received_amount > receivable_detail.amount:
                    #如果有商品是部分收款P，就算是有超额收款也还是算成P
                    if status is 'P':
                        status = 'P'
                    else:
                        status = 'O'

        receivable.status = status
        receivable.save()

        #修改收款单状态是否有延迟
        receive = form.save(commit=False)
        today = datetime.datetime.now().date()
        if today > receivable.receivabled:
            receive.is_delay = True
        receive.save()


admin.site.register(Receive, ReceiveAdmin)


class DueDetailInline(admin.TabularInline):
    model = DueDetail
    fields = ['material', 'amount', 'currency']
    extra = 0


class DueAdmin(admin.ModelAdmin):
    list_display = ['id', 'arrive', 'supplier', 'is_active', 'status', 'dued', 'created', 'create_user']
    fields = ['arrive', 'supplier', 'is_active', 'status', 'dued', 'create_user']
    inlines = [DueDetailInline]
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'dued'


admin.site.register(Due, DueAdmin)


"""
付款单单身检查
1.最少要有一个单身
2.付款金额是否至少一笔大于0
3.付款金额不得是负数
4.单身原料不得重复
"""
class PayDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        detail_count = 0
        detail_amount = 0

        material_list = []
        for form in self.forms:
            if form.cleaned_data:
                detail_count += 1

                amount = form.cleaned_data.get('amount')
                if amount < 0:
                    raise forms.ValidationError(u'收款单中收款金额不得为负数。')
                elif amount > 0:
                    detail_amount += 1

                material = form.cleaned_data.get('material')
                if material.id in material_list:
                    raise forms.ValidationError(u"单身原料[{}-{}]付款已重复，"
                                                u"请重新填写付货单。".format(material.id, material.title))
                else:
                    material_list.append(material.id)

        if detail_count < 1:
            raise forms.ValidationError(u'您必须最少输入一笔付款单单身')
        if detail_amount < 1:
            raise forms.ValidationError(u'您必须最少一笔收款单单身金额大于0')


class PayDetailInline(admin.TabularInline):
    formset = PayDetailCheckInlineFormset
    model = PayDetail
    fields = ['material', 'amount', 'discount', 'currency', 'rate', 'description']
    raw_id_fields = ['material', 'currency']
    extra = 0


"""
付款时的相关动作如下：
1.检查付款日期是否有延迟(is_delay)
2.检查应付帐款金额是否满足，决定应付帐款"状态"，('A', u'全部付款'),('P', u'部分付款'),('O', '超额付款')
3.更新采购单单身的已付含税金额(tax_pay)
4.付款单身如果有金额是0的则不存入数据库
"""
class PayAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_no', 'due', 'supplier', 'is_active', 'is_delay', 'created', 'create_user']
    fields = ['due', 'invoice_no']
    inlines = [PayDetailInline]
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'due':
            kwargs['queryset'] = Due.objects.filter(is_active=True).exclude(status='A')
        return super(PayAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
            due = obj.due
            obj.supplier = due.supplier
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        #决定对应应付帐款状态('A', '全部付款'),('P', '部分付款')，('O', '超额付款')
        # 如果有一个应付帐款单身金额是超额付款的话，则状态为O
        due = form.cleaned_data.get('due')
        arrive = due.arrive
        procurement = arrive.procurement
        due_details = DueDetail.objects.filter(due=due)
        pays = Pay.objects.filter(due=due)
        status = 'A'
        for due_detail in due_details:
            material = due_detail.material
            procurement_materials = ProcurementMaterial.objects.filter(procurement=procurement, material=material)
            paid_amount = 0
            if procurement_materials.count() > 0:
                procurement_material = procurement_materials[0]
                for pay in pays.all():
                    pay_details = PayDetail.objects.filter(material=material, pay=pay)
                    if pay_details.all().count() > 0:
                        for pay_detail in pay_details.all():
                            paid_amount += pay_detail.amount + pay_detail.discount

            if paid_amount > due_detail.amount:
                status = 'O'
            else:
                if paid_amount < due_detail.amount:
                    #如果有商品是超额付款O，就算是有部分款也还是算成O
                    if status is 'O':
                        status = 'O'
                    else:
                        status = 'P'

        due.status = status
        due.save()

        #修改付款单状态是否有延迟
        pay = form.save(commit=False)
        today = datetime.datetime.now().date()
        if today > due.dued:
            pay.is_delay = True
        pay.save()


admin.site.register(Pay, PayAdmin)

