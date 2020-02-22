from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Due, DueDetail, Pay, PayDetail, Receivable, ReceivableDetail, Receive, ReceiveDetail


def receivable_ajax_detail_list(request):
    return_dict = {}
    #判断使用者是否有权限检视应收帐款
    if request.user.has_perm('finance.view_receivable'):
        receivable_id = request.GET.get('id')
        receivable = Receivable.objects.get(id=receivable_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['receivables'] = []
        receivable_details = ReceivableDetail.objects.filter(receivable=receivable)

        for d in receivable_details.all():
            product = d.product
            amount = d.amount
            currency = d.currency
            rate = currency.rate

            # 如果该应收帐款有其他对应收款，则需扣掉已收款的商品金额
            other_receives = Receive.objects.filter(receivable=receivable, is_active=True)
            if other_receives.count() > 0:
                return_dict['msg'] = u'此应收帐款已有对应收款单，收款单单号如下：'
                for r in other_receives.all():
                    return_dict['msg'] += ' ' + str(r.id)
                    receive_detail = ReceiveDetail.objects.filter(receive=r, product=product)
                    if receive_detail.all().count() > 0:
                        amount -= receive_detail[0].amount

            if amount != 0:
                product_info = {'id': product.id, 'title': product.title}
                product_dict = {'product': product_info, 'amount': amount, 'currency': currency.id, 'rate': rate}
                return_dict['receivables'].append(product_dict)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览应收帐款"
    return JsonResponse(return_dict)


def due_ajax_detail_list(request):
    return_dict = {}
    #判断使用者是否有权限检视应付帐款
    if request.user.has_perm('finance.view_due'):
        due_id = request.GET.get('id')
        due = Due.objects.get(id=due_id)
        return_dict['code'] = 0
        return_dict['msg'] = ''
        return_dict['dues'] = []
        due_details = DueDetail.objects.filter(due=due)

        for d in due_details.all():
            material = d.material
            amount = d.amount
            currency = d.currency
            rate = currency.rate

            # 如果该应付帐款有其他对应付款，则需扣掉已付款的金额
            other_pays = Pay.objects.filter(due=due, is_active=True)
            if other_pays.count() > 0:
                return_dict['msg'] = u'此应付帐款已有对应付款单，付款单号如下：'
                for p in other_pays.all():
                    return_dict['msg'] += ' ' + str(p.id)
                    pay_detail = PayDetail.objects.filter(pay=p, material=material)
                    if pay_detail.all().count() > 0:
                        amount -= pay_detail[0].amount

            if amount != 0:
                material_info = {'id': material.id, 'title': material.title}
                material_dict = {'material': material_info, 'amount': amount, 'currency': currency.id, 'rate': rate}
                return_dict['dues'].append(material_dict)
    else:
        return_dict['code'] = 1
        return_dict['msg'] = u"您无权限浏览应付帐款"
    return JsonResponse(return_dict)

