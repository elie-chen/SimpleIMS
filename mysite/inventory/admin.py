from django import forms
from django.contrib import admin
from .models import Mcheck, McheckDetail, Mtran, Pcheck, PcheckDetail, Process, ProcessDetail, Ptran
from basic.models import Product

class MtranAdmin(admin.ModelAdmin):
    list_display = ['id', 'material', 'source_form', 'source_id', 'from_quantity', 'tran_quantity',
                    'to_quantity', 'created', 'create_user']
    list_filter = ['material']
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'


admin.site.register(Mtran, MtranAdmin)


class PtranAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'source_form', 'source_id', 'from_quantity', 'tran_quantity',
                    'to_quantity', 'created', 'create_user']
    list_filter = ['product']
    view_on_site = False
    list_per_page = 10
    list_max_show_all = 100
    date_hierarchy = 'created'


admin.site.register(Ptran, PtranAdmin)


"""
原料库存异动申请单单身检查
1.最少要有一个单身
2.单身中原料不得重复
3.单身异动数量不得为0
4.单身原料异动后的库存数量不得小于0
"""
class McheckDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        material_list = []
        for form in self.forms:
            if form.cleaned_data:
                count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity == 0:
                    raise forms.ValidationError(u'原料库存异动申请单中单身数量不得为0。')

                material = form.cleaned_data.get('material')
                if material.stock + quantity < 0:
                    raise forms.ValidationError(u"单身原料[{}-{}]库存量为 {}，加上异动量 {} "
                                                u"后库存小于0不合法，请重新填写单身中的异动"
                                                u"数量。".format(material.id, material.title, material.stock, quantity))

                if material.id in material_list:
                    raise forms.ValidationError(u"单身原料[{}-{}]已重复，"
                                                u"请重新填写原料库存异动申请单。".format(material.id, material.title))
                else:
                    material_list.append(material.id)
        if count < 1:
            raise forms.ValidationError(u'您必须最少输入一笔原料库存异动申请单单身')


class McheckDetailInline(admin.TabularInline):
    formset = McheckDetailCheckInlineFormset
    model = McheckDetail
    fields = ['material', 'quantity']
    raw_id_fields = ['material']
    extra = 0


class McheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'description', 'created', 'create_user']
    fields = ['description']
    inlines = [McheckDetailInline]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        mcheck = form.save(commit=False)

        mcheck_details = McheckDetail.objects.filter(mcheck=mcheck)
        for mcheck_detail in mcheck_details.all():
            #新增原料库存异动
            material = mcheck_detail.material
            stock = material.stock
            tran_quantity = mcheck_detail.quantity

            mtran = Mtran()
            mtran.material = material
            mtran.source_form = 'MCHECK'
            mtran.source_id = mcheck.id
            mtran.from_quantity = stock
            mtran.tran_quantity = tran_quantity
            mtran.to_quantity = stock + tran_quantity
            mtran.create_user = request.user
            mtran.save()

            #异动原料库存量
            material.stock = stock + tran_quantity
            material.save()

        #如果没有发生错误则修改原料库存异动申请单状态
        mcheck.is_active = True
        mcheck.save()


admin.site.register(Mcheck, McheckAdmin)


"""
商品库存异动申请单单身检查
1.最少要有一个单身
2.单身中商品不得重复
3.单身异动数量不得为0
4.单身商品异动后的库存数量不得小于0
"""
class PcheckDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        product_list = []
        for form in self.forms:
            if form.cleaned_data:
                count += 1

                quantity = form.cleaned_data.get('quantity')
                if quantity == 0:
                    raise forms.ValidationError(u'商品库存异动申请单中单身数量不得为0。')

                product = form.cleaned_data.get('product')
                if product.stock + quantity < 0:
                    raise forms.ValidationError(u"单身商品[{}-{}]库存量为 {}，加上异动量 {} "
                                                u"后库存小于0不合法，请重新填写单身中的异动"
                                                u"数量。".format(product.id, product.title, product.stock, quantity))

                if product.id in product_list:
                    raise forms.ValidationError(u"单身商品[{}-{}]已重复，"
                                                u"请重新填写商品库存异动申请单。".format(product.id, product.title))
                else:
                    product_list.append(product.id)
        if count < 1:
            raise forms.ValidationError(u'您必须最少输入一笔商品库存异动申请单单身')


class PcheckDetailInline(admin.TabularInline):
    formset = PcheckDetailCheckInlineFormset
    model = PcheckDetail
    fields = ['product', 'quantity']
    raw_id_fields = ['product']
    extra = 0


class PcheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_active', 'description', 'created', 'create_user']
    fields = ['description']
    inlines = [PcheckDetailInline]
    view_on_site = False

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        pcheck = form.save(commit=False)

        pcheck_details = PcheckDetail.objects.filter(pcheck=pcheck)
        for pcheck_detail in pcheck_details.all():
            #新增商品库存异动
            product = pcheck_detail.product
            stock = product.stock
            tran_quantity = pcheck_detail.quantity

            ptran = Ptran()
            ptran.product = product
            ptran.source_form = 'PCHECK'
            ptran.source_id = pcheck.id
            ptran.from_quantity = stock
            ptran.tran_quantity = tran_quantity
            ptran.to_quantity = stock + tran_quantity
            ptran.create_user = request.user
            ptran.save()

            #异动商品库存量
            product.stock = stock + tran_quantity
            product.save()

        #如果没有发生错误则修改商品库存异动申请单状态
        pcheck.is_active = True
        pcheck.save()


admin.site.register(Pcheck, PcheckAdmin)


"""
制程单单身检查
1.最少要有一个单身
"""
class ProcessDetailCheckInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        count = 0
        product_list = []
        for form in self.forms:
            if form.cleaned_data:
                count += 1

        if count < 1:
            raise forms.ValidationError(u'此商品无制程BOM表资料，请修改好该商品BOM表数据再填写制程单')


class ProcessDetailInline(admin.TabularInline):
    formset = ProcessDetailCheckInlineFormset
    model = ProcessDetail
    fields = ['material', 'quantity']
    raw_id_fields = ['material']
    extra = 0


class ProcessAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'description', 'status', 'claimed',
                    'receipted', 'created', 'create_user']
    fields = ['order', 'product', 'quantity', 'description']
    inlines = [ProcessDetailInline]
    view_on_site = False
    list_filter = ['order', 'product', 'status']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.create_user = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if not change:
            process = form.save(commit=False)

            instances = formset.save(commit=False)
            for instance in instances:
                instance.quantity = instance.quantity * process.quantity

            super().save_formset(request, form, formset, change)


admin.site.register(Process, ProcessAdmin)

