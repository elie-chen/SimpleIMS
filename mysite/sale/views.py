from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Order, OrderProduct, Ship, ShipDetail


def order_ajax_product_list(request):
    return_dict = {}
    #判断用户是否有权限检视订单
    if request.user.has_perm('sale.view_order'):
        order_id = request.GET.get('id')
        order = Order.objects.get(id=order_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['products'] = []
        order_products = OrderProduct.objects.filter(order=order)

        for p in order_products.all():
            product = p.product
            quantity = p.quantity

            # 如果该订单有其他对应出货单，则需扣掉已出货的商品数量
            ships = Ship.objects.filter(order=order, is_active=True)
            if ships.count() > 0:
                return_dict['msg'] = u'此订单已有对应出货单，出货单单号如下：'
                for s in ships.all():
                    return_dict['msg'] += ' ' + str(s.id)
                    ship_product = ShipDetail.objects.filter(ship=s, product=product)
                    if ship_product.all().count() > 0:
                        quantity -= ship_product[0].quantity

            product_info = {}
            product_info['id'] = product.id
            product_info['title'] = product.title
            product_dict = {'product': product_info, 'quantity': quantity}
            return_dict['products'].append(product_dict)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览订单"
    return JsonResponse(return_dict)

