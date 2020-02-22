from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Mtran, Ptran, Process, ProcessDetail
from basic.models import Bom, Product
from sale.models import Order, OrderProduct
import datetime

def process_ajax_order_product_list(request):
    return_dict = {}
    #判断使用者是否有权限检视制程单
    if request.user.has_perm('inventory.view_process'):
        order_id = request.GET.get('id')
        order = Order.objects.get(id=order_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['products'] = []
        order_products = OrderProduct.objects.filter(order=order)

        for p in order_products.all():
            product = p.product
            product_info = {}
            product_info['id'] = product.id
            product_info['title'] = product.title
            return_dict['products'].append(product_info)

        other_processes = Process.objects.filter(order=order)
        if other_processes.count() > 0:
            return_dict['msg'] = u'该订单已有其他制程单，制程单号(商品名称)：'
            for p in other_processes.all():
                other_product = p.product
                return_dict['msg'] += ' {}({})'.format(str(p.id), other_product.title)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览制程单"
    return JsonResponse(return_dict)


def process_ajax_bom_list(request):
    return_dict = {}
    #判断使用者是否有权限检视制程单
    if request.user.has_perm('inventory.view_process'):
        order_id = request.GET.get('order_id')
        order = Order.objects.get(id=order_id)
        product_id = request.GET.get('product_id')
        product = Product.objects.get(id=product_id)
        boms = Bom.objects.filter(product=product)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['boms'] = []

        order_products = OrderProduct.objects.filter(order=order, product=product)
        if order_products.count() > 0:
            return_dict['quantity'] = order_products[0].quantity
        else:
            return_dict['quantity'] = 0

        for b in boms.all():
            material = b.material
            quantity = b.quantity
            material_info = {}
            material_info['id'] = material.id
            material_info['title'] = material.title
            material_dict = {'material': material_info, 'quantity': quantity}
            return_dict['boms'].append(material_dict)

    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览制程单"
    return JsonResponse(return_dict)


def process_ajax_status(request):
    return_dict = {}
    #判断使用者是否有权限检视制程单
    if request.user.has_perm('inventory.view_process'):
        process_id = request.GET.get('id')
        process = Process.objects.get(id=process_id)
        return_dict['code'] = 0
        return_dict['status'] = process.status

    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览制程单"
    return JsonResponse(return_dict)


def process_ajax_claim_material(request):
    return_dict = {}
    #判断使用者是否有权限检视制程单
    if request.user.has_perm('inventory.view_process'):
        process_id = request.GET.get('id')
        process = Process.objects.get(id=process_id)
        process_details = ProcessDetail.objects.filter(process=process)
        if process_details.count() > 0:
            stock_enough_bool = True
            for process_detail in process_details:
                quantity = process_detail.quantity
                material = process_detail.material
                if material.stock < quantity:
                    return_dict['code'] = 1
                    return_dict['msg'] = '原料[{}-{}]库存量只有{}，不足领出量{}'.format(material.id, material.title, material.stock, quantity)
                    stock_enough_bool = False

            if stock_enough_bool:
                for process_detail in process_details:
                    quantity = process_detail.quantity
                    material = process_detail.material

                    mtran = Mtran()
                    mtran.material = material
                    mtran.source_form = 'PROCESS'
                    mtran.source_id = process_id
                    mtran.from_quantity = material.stock
                    mtran.tran_quantity = 0 - quantity
                    mtran.to_quantity = material.stock - quantity
                    mtran.create_user = request.user
                    mtran.save()

                    material.stock = material.stock - quantity
                    material.save()

                process.status = 'C'
                process.claimed = datetime.datetime.now()
                process.claim_user = request.user
                process.save()

                return_dict['code'] = 0
                return_dict['msg'] = u"原料出库已确认完毕"

        else:
            return_dict['code'] = 1
            return_dict['msg'] = u"该制程单无单身资料"

    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览制程单"
    return JsonResponse(return_dict)


def process_ajax_receipt_product(request):
    return_dict = {}
    #判断使用者是否有权限检视制程单
    if request.user.has_perm('inventory.view_process'):
        process_id = request.GET.get('id')
        process = Process.objects.get(id=process_id)
        product = process.product
        quantity = process.quantity

        ptran = Ptran()
        ptran.product = product
        ptran.source_form = 'PROCESS'
        ptran.source_id = process_id
        ptran.from_quantity = product.stock
        ptran.tran_quantity = quantity
        ptran.to_quantity = product.stock + quantity
        ptran.create_user = request.user
        ptran.save()

        product.stock = product.stock + quantity
        product.save()

        process.status = 'R'
        process.receipted = datetime.datetime.now()
        process.receipt_user = request.user
        process.save()

        return_dict['code'] = 0
        return_dict['msg'] = u"商品入库已确认完毕"

    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览制程单"
    return JsonResponse(return_dict)

