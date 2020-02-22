from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_permission_codename
import datetime
from .models import Arrive, ArriveDetail, Procurement, ProcurementMaterial
from finance.models import Due, DueDetail
from inventory.models import Mtran

"""
采购单单身检查
1.最少要有一个单身
2.原料不可重复
3.原料数量是否是否至少一笔大于0
4.原料数量不得是负数
"""
class ProcurementMaterialCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        detail_count = 0
        detail_amount = 0

        material_list = []
        for form in self.forms:
            if form.cleaned_data:
                detail_count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity < 0:
                    raise forms.ValidationError(u'采购单中原料数量不得为负数。')
                elif quantity > 0:
                    detail_amount += 1

                material = form.cleaned_data.get('material')
                if material.id in material_list:
                    raise forms.ValidationError(u"单身原料[{}-{}]已重复，"
                                                u"请重新填写采购单。".format(material.id, material.title))
                else:
                    material_list.append(material.id)

        if detail_count < 1:
            raise forms.ValidationError(u'您最少必须输入一笔采购单单身。')
        if detail_amount < 1:
            raise forms.ValidationError(u'您必须最少一笔采购单单身数量大于0')


class ProcurementMaterialInline(admin.TabularInline):
    formset = ProcurementMaterialCheckInlineFormset
    model = ProcurementMaterial
    fields = ['material', 'quantity', 'description']
    raw_id_fields = ['material']
    extra = 0


class ProcurementAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_correspond', 'order', 'supplier', 'is_active', 'status', 'etd', 'created', 'create_user']
    fields = ['is_correspond', 'order', 'supplier', 'etd']
    actions = ['make_actived']
    inlines = [ProcurementMaterialInline]
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
        super().save_model(request, obj, form, change)

    def make_actived(self, request, queryset):
        rows = queryset.update(is_active=False)
        if rows > 0:
            self.message_user(request, u'已完成终止采购单动作')
    make_actived.allowed_permissions = ('active',)
    make_actived.short_description = u'终止采购单'

    def has_active_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('active', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Procurement, ProcurementAdmin)


"""
到货单单身检查
1.最少要有一个单身
2.原料不可重复
3.原料数量至少一笔大于0
4.原料数量不得为负数
"""
class ArriveDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        detail_count = 0
        detail_amount = 0

        material_list = []
        for form in self.forms:
            if form.cleaned_data:
                detail_count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity < 0:
                    raise forms.ValidationError(u'到货单中原料数量不得为负数。')
                elif quantity > 0:
                    detail_amount += 1

                material = form.cleaned_data.get('material')
                if material.id in material_list:
                    raise forms.ValidationError(u"单身原料[{}-{}]到货已重复，"
                                                u"请重新填写到货单。".format(material.id, material.title))
                else:
                    material_list.append(material.id)

        if detail_count < 1:
            raise forms.ValidationError(u'您最少必须输入一笔到货单单身。')
        if detail_amount < 1:
            raise forms.ValidationError(u'您必须最少一笔到款单单身数量大于0')


class ArriveDetailInline(admin.TabularInline):
    formset = ArriveDetailCheckInlineFormset
    model = ArriveDetail
    fields = ['material', 'quantity', 'description']
    raw_id_fields = ['material']
    extra = 0


class ArriveAdmin(admin.ModelAdmin):
    list_display = ['id', 'procurement', 'supplier', 'is_active', 'is_delay', 'created', 'create_user']
    fields = ['procurement']
    actions = ['make_actived']
    inlines = [ArriveDetailInline]
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'procurement':
            kwargs['queryset'] = Procurement.objects.filter(is_active=True).exclude(status='A')
        return super(ArriveAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
            procurement = obj.procurement
            obj.supplier = procurement.supplier
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        arrive = form.save(commit=False)

        # 新增应付帐款单头
        due = Due()
        due.arrive = arrive
        due.supplier = arrive.supplier
        # 应付日期=到货日期 + 帐期
        due.dued = arrive.created + datetime.timedelta(days=arrive.supplier.period.period)
        due.create_user = arrive.create_user
        due.save()

        arrive_details = ArriveDetail.objects.filter(arrive=arrive)
        for arrive_detail in arrive_details:
            # 新增原料库存异动
            material = arrive_detail.material
            stock = material.stock
            tran_quantity = arrive_detail.quantity

            mtran = Mtran()
            mtran.material = material
            mtran.source_form = 'ARRIVE'
            mtran.source_id = arrive.id
            mtran.from_quantity = stock
            mtran.tran_quantity = tran_quantity
            mtran.to_quantity = stock + tran_quantity
            mtran.create_user = request.user
            mtran.save()

            # 新增应付帐款单身
            due_detail = DueDetail()
            due_detail.due = due
            due_detail.material = material
            due_detail.amount = material.tax_price * tran_quantity
            due_detail.currency = material.currency
            due_detail.save()

            # 增加商品库存量
            material.stock = stock + tran_quantity
            material.save()

        procurement = form.cleaned_data.get('procurement')
        # 修改到货单状态
        arrive.is_active = True
        today = datetime.datetime.now().date()
        if today > procurement.etd:
            procurement.is_delay = True
        procurement.save()

        # 决定对应采购单状态('A', '全部到货'),('P', '部分到货')，('O', '超额到货')如果有一个采购单单身数量没有全部出完的话，则状态为P
        procurement_materials = ProcurementMaterial.objects.filter(procurement=procurement)
        arrives = Arrive.objects.filter(procurement=procurement)
        status = 'A'
        for procurement_material in procurement_materials:
            material = procurement_material.material
            arrived_quantity = 0
            for arrive in arrives.all():
                arrive_details = ArriveDetail.objects.filter(material=material, arrive=arrive)
                if arrive_details.all().count() > 0:
                    for arrive_detail in arrive_details.all():
                        arrived_quantity += arrive_detail.quantity

            if arrived_quantity < procurement_material.quantity:
                status = 'P'
            else:
                if arrived_quantity > procurement_material.quantity:
                    # 如果有商品是部分到货P，就算是有超额到货也还是算成P
                    if status is 'P':
                        status = 'P'
                    else:
                        status = 'O'

        procurement.status = status
        procurement.save()

        # 如果没有发生错误则修改应付帐款状态
        due.is_active = True
        due.save()

    def make_actived(self, request, queryset):
        rows = queryset.update(is_active=False)
        if rows > 0:
            self.message_user(request, u'已完成终止到货单动作')
    make_actived.allowed_permissions = ('active',)
    make_actived.short_description = u'终止到货单'

    def has_active_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('active', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Arrive, ArriveAdmin)

