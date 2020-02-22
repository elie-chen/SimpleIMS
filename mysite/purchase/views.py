from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Arrive, ArriveDetail, Procurement, ProcurementMaterial
from basic.models import Bom, Supplier
from sale.models import Order, OrderProduct


def procurement_ajax_supplier_list(request):
    return_dict = {}
    #判断使用者是否有权限检视采购单
    if request.user.has_perm('purchase.view_procurement'):
        order_id = request.GET.get('id')
        order = Order.objects.get(id=order_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['suppliers'] = []
        order_products = OrderProduct.objects.filter(order=order)

        other_procurements = Procurement.objects.filter(order=order)
        if other_procurements.count() > 0:
            return_dict['msg'] = u'此订单已有对应采购单，采购单单号如下：'
            for p in other_procurements:
                return_dict['msg'] += ' ' + str(p.id) + u'(供货商:{})'.format(p.supplier.title)

        for p in order_products.all():
            product = p.product
            boms = Bom.objects.filter(product=product)
            for b in boms.all():
                material = b.material
                supplier = material.supplier
                if supplier.id not in return_dict['suppliers']:
                    return_dict['suppliers'].append(supplier.id)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览采购单"
    return JsonResponse(return_dict)


def procurement_ajax_material_list(request):
    return_dict = {}
    #判断使用者是否有权限检视采购单
    if request.user.has_perm('purchase.view_procurement'):
        order_id = request.GET.get('order_id')
        order = Order.objects.get(id=order_id)
        supplier_id = request.GET.get('supplier_id')
        supplier = Supplier.objects.get(id=supplier_id)
        return_dict['code'] = 0
        return_dict['materials'] = []
        order_products = OrderProduct.objects.filter(order=order)
        products = []
        if order_products.count() > 0:
            for order_product in order_products:
                products.append(order_product.product)
        other_procurements = Procurement.objects.filter(order=order)

        boms = Bom.objects.filter(product__in=products)
        """
        有可能不同商品有相同的组成原料，如下：
        id  product_id  material_id quantity    status
        1   1           1           2           A
        2   1           2           3           A
        3   2           1           5           A
        4   2           2           5           A
        """
        material_list = []
        for b in boms.all():
            material = b.material
            if material.supplier == supplier:
                if b.material not in material_list:
                    material_list.append(material)

        for material in material_list:
            #采购单中该原料采购数量 = 订单中的商品数量*BOM表中该商品的原料组成数量
            # 扣除 其他对应到该订单的采购单的相同原料的采购数量
            # 再扣除 该原料库存
            quantity = 0
            for order_product in order_products.all():
                bom = boms.filter(product=order_product.product, material=material)
                if bom.count() > 0:
                    quantity += order_product.quantity * bom[0].quantity

            if other_procurements.count() != 0:
                other_procurement_materials = ProcurementMaterial.objects.filter(procurement__in=other_procurements, material=material)
                if other_procurement_materials.count() != 0:
                    for m in other_procurement_materials.all():
                        quantity -= m.quantity

            quantity -= material.stock

            if quantity > 0:
                material_info = {'id': material.id, 'title': material.title, 'quantity': quantity}
                return_dict['materials'].append(material_info)

    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览采购单"
    return JsonResponse(return_dict)


def procurement_ajax_list(request):
    return_dict = {}
    #判断使用者是否有权限检视采购单
    if request.user.has_perm('purchase.view_procurement'):
        procurement_id = request.GET.get('id')
        procurement = Procurement.objects.get(id=procurement_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['materials'] = []
        procurement_materials = ProcurementMaterial.objects.filter(procurement=procurement)

        for m in procurement_materials.all():
            material = m.material
            quantity = m.quantity

            # 如果该采购单有其他对应进货单，则需扣掉已进货的原料数量
            arrives = Arrive.objects.filter(procurement=procurement, is_active=True)
            if arrives.count() > 0:
                return_dict['msg'] = u'此采购单已有对应到货单，到货单单号如下：'
                for a in arrives.all():
                    return_dict['msg'] += ' ' + str(a.id)
                    arrive_material = ArriveDetail.objects.filter(arrive=a, material=material)
                    if arrive_material.all().count() > 0:
                        quantity -= arrive_material[0].quantity

            material_info = {}
            material_info['id'] = material.id
            material_info['title'] = material.title
            material_dict = {'material': material_info, 'quantity': quantity}
            return_dict['materials'].append(material_dict)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览采购单"
    return JsonResponse(return_dict)

