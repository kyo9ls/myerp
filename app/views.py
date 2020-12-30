from django.shortcuts import render, HttpResponse, redirect
from app import models
from django.views import View
from app.utils import gen_md5_digest, Pagination, user_id, get_date
import json, os
from django.db.models import Sum, F, Q
from django.db import transaction
from decimal import Decimal
import base64



# Create your views here.
def create_excel(select_dict, is_all_company=False, user=''):
    import xlwt
    import datetime
    thead = ['日期', '公司', '供应商', '客户', '商品', '售价', '数量', '车号', '运费', '代理', '佣金']
    tdata = ['order_date', 'company__name', 'supplier__name', 'client__name',
             'good__name', 'goods_price', 'number', 'driver__name', 'driver_price',
             'sale__name', 'sale_price']
    tdic = dict(zip(thead, tdata))
    file_name = '/excel/%s.xls' % (datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    # 文件路径
    file_path = os.path.abspath('.') + file_name
    # excel格式
    common_style = xlwt.XFStyle()
    date_style = xlwt.XFStyle()
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    common_style.borders = borders
    date_style.borders = borders
    date_style.num_format_str = 'yyyy"年"m"月"d"日"'
    wb = xlwt.Workbook(encoding='utf-8')  # 创建Excel
    if not is_all_company:
        ws = wb.add_sheet('sheet1', True)  # 创建sheet
        orders = models.Order.objects.values_list(*tdic.values()).filter(**select_dict).distinct().order_by(
            'order_date')
        # 写入表头
        ws.write(0, 0, '序号')
        for i in range(len(thead)):
            ws.write(0, i + 1, thead[i])
        # 写入数据
        count = 1  # 序号
        for i in range(len(orders)):
            ws.write(i + 1, 0, count, common_style)
            for j in range(len(orders[i])):
                ws.write(i + 1, j + 1, orders[i][j], date_style if j == 0 else common_style)
            count += 1
        ws.col(1).width = 4000
        ws.col(2).width = 5000
        ws.col(8).width = 3000
        wb.save(file_path)
        return file_path
    else:
        all_company = models.Company.objects.values_list('no', 'name').filter(user_id=user)
        for company in all_company:
            ws = wb.add_sheet(company[1], True)  # 创建sheet
            select_dict['company_id'] = company[0]
            orders = models.Order.objects.values_list(*tdic.values()).filter(**select_dict).distinct().order_by(
                'order_date')
            # 写入表头
            ws.write(0, 0, '序号')
            for i in range(len(thead)):
                ws.write(0, i + 1, thead[i])
            # 写入数据
            count = 1  # 序号
            for i in range(len(orders)):
                ws.write(i + 1, 0, count, common_style)
                for j in range(len(orders[i])):
                    ws.write(i + 1, j + 1, orders[i][j], date_style if j == 0 else common_style)
                count += 1
            ws.col(1).width = 4000
            ws.col(2).width = 5000
            ws.col(8).width = 3000
            wb.save(file_path)
        return file_path


def download(request):
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取订单
    select_dict = {}
    select_dict['company__user_id'] = user
    select_dict['company_id'] = request.GET.get('com_no')
    select_dict['supplier_id'] = request.GET.get('sup_no')
    select_dict['client_id'] = request.GET.get('cli_no')
    select_dict['driver_id'] = request.GET.get('dri_no')
    select_dict['sale_id'] = request.GET.get('sale_no')
    select_dict['order_date__gte'] = request.GET.get('start')
    select_dict['order_date__lte'] = request.GET.get('end')
    for key in list(select_dict):
        if not select_dict[key]:
            del select_dict[key]
    try:
        file_path = create_excel(select_dict)
        from django.http import StreamingHttpResponse

        def file_iterator(file_name):
            with open(file_name, 'rb')as f:
                while True:
                    c = f.read(512)
                    if c:
                        yield c
                    else:
                        break

        response = StreamingHttpResponse(file_iterator(file_path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = "attachment;filename={0}".format(file_path.split('/')[-1])
        return response
    except Exception as e:
        return HttpResponse('导出失败\n' + str(e))


# 登录
def login(request):
    hint = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            password = gen_md5_digest(password)
            user = models.User.objects.filter(username=username, password=password).first()
            if user:
                request.session['userid'] = user.no
                request.session['username'] = user.username
                return redirect('/supplier_list/')
            else:
                hint = '用户名或密码错误'
        else:
            hint = '请输入有效的用户名和密码'
    return render(request, 'login.html', {'hint': hint})

    # 注销


# 注销
def logout(request):
    request.session.flush()
    return redirect('/login/')

    # 展示供应商


# 供应商列表
def supplier_list(request):
    # 获取用户id
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取供应商信息
    all_suppliers = models.Supplier.objects.filter(company__user__no=user).distinct()
    # 页码
    count = all_suppliers.count()
    page = Pagination(request, count)
    # 返回一个含有供应商信息的页面
    return render(request, 'supplier_list.html',
                  {'all_suppliers': all_suppliers[page.start:page.end], 'page_html': page.page_html})


# 增加供应商
class SupplierAdd(View):

    # get 请求
    def get(self, request):
        # 获取用户ID
        if user_id(request):
            user = user_id(request)
        else:
            return redirect('/login/')
        # 获取对应公司
        com = models.Company.objects.filter(user=user)
        return render(request, 'supplier_add.html', {'com': com})

    # post请求
    def post(self, request):
        # post请求
        # 获取用户输入的数据
        sup_name = request.POST.get('sup_name')
        com_no = request.POST.get('com_no')
        # 获取用户ID
        user = user_id(request)
        com = models.Company.objects.filter(user=user)
        if not sup_name:
            return render(request, 'supplier_add.html', {'error': '供应商名称不能为空', 'com': com})
        elif models.Supplier.objects.filter(name=sup_name, company__no=com_no):
            return render(request, 'supplier_add.html', {'error': '记录已经存在', 'com': com})
        elif models.Supplier.objects.filter(name=sup_name) and (not models.Supplier.objects.filter(name=sup_name,
                                                                                                   company__no=com_no)):
            # 供应商存在，但关联关系不存在，新增关联关系
            with transaction.atomic():
                sup_obj = models.Supplier.objects.filter(name=sup_name).first()
                sup_obj.company_set.add(com_no)
                models.Advpayment.objects.create(company_id=com_no, supplier_id=sup_obj.no)
            return redirect('/supplier_list/')
        else:
            # 将数据新增到数据库中
            sup_obj = models.Supplier.objects.create(name=sup_name)
            sup_obj.company_set.add(com_no)
            models.Advpayment.objects.create(supplier_id=sup_obj.no, company_id=com_no)
            # 返回一个重定向到展示供应商的页面
            return redirect('/supplier_list/')


# 编辑供应商和公司
def supplier_edit(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取供应商及公司编号
    sup_no = request.GET.get('sup_no')
    try:
        sup_obj = models.Supplier.objects.filter(no=sup_no, company__user_id=user).first()
        # 获取post请求
        # 获取用户输入数据
        if request.method == 'POST':
            sup_name = request.POST.get('sup_name')
            # 名称为空
            if not sup_name:
                return render(request, 'supplier_edit.html', {'error': '名称不能为空', 'sup_obj': sup_obj})
            # 名称重复
            elif models.Supplier.objects.filter(name=sup_name):
                return render(request, 'supplier_edit.html', {'error': '名称重复', 'sup_obj': sup_obj})
            else:
                with transaction.atomic():
                    sup_obj.name = sup_name
                    sup_obj.save()
                return redirect('/supplier_list/')

        else:
            return render(request, 'supplier_edit.html', {'sup_obj': sup_obj, })
    except Exception as e:
        return HttpResponse(str(e))


# 预付款表
def adv_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取供应商信息
    sup_no = request.GET.get('sup_no')
    all_advs = models.Advpayment.objects.filter(supplier=sup_no, company__user_id=user)
    # 返回页面
    return render(request, 'adv_list.html', {'all_advs': all_advs, })


# 客户列表
def client_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取供应商信息
    all_clients = models.Client.objects.filter(company__user=user).distinct()
    # 页码
    count = all_clients.count()
    page = Pagination(request, count)
    # 返回页面
    return render(request, 'client_list.html',
                  {'all_clients': all_clients[page.start:page.end],
                   'page_html': page.page_html})


# 增加客户
class ClientAdd(View):
    # get 请求
    def get(self, request):
        # 获取用户ID
        if user_id(request):
            user = user_id(request)
        else:
            return redirect('/login/')
        com = models.Company.objects.filter(user__no=user)
        return render(request, 'client_add.html', {'com': com})

    # post请求
    def post(self, request):
        # post请求
        # 获取用户输入的数据
        cli_name = request.POST.get('cli_name')
        com_no = request.POST.get('com_no')
        # 获取用户ID
        if user_id(request):
            user = user_id(request)
        else:
            return redirect('/login/')
        com = models.Company.objects.filter(user__no=user)
        try:
            if not cli_name:
                return render(request, 'client_add.html', {'error': '客户名称不能为空', 'com': com})
            elif models.Client.objects.filter(name=cli_name, company__no=com_no):
                # 客户及关联关系已经存在
                return render(request, 'client_add.html', {'error': '客户已经存在', 'com': com})
            elif models.Client.objects.filter(name=cli_name) and (not models.Client.objects.filter(name=cli_name,
                                                                                                   company__no=com_no)):
                # 客户存在，但关联关系不存在，新增关联关系
                cli_obj = models.Client.objects.get(name=cli_name)
                cli_obj.company_set.add(com_no)
                models.Debt.objects.create(company_id=com_no, client_id=cli_obj.no)
                return redirect('/client_list/')
            else:
                # 客户不存在
                # 将数据新增到数据库中
                with transaction.atomic():
                    cli_obj = models.Client.objects.create(name=cli_name)
                    cli_obj.company_set.add(com_no)
                    models.Debt.objects.create(company_id=com_no, client_id=cli_obj.no)
                # 返回一个重定向到展示供应商的页面
                return redirect('/client_list/')
        except Exception as e:
            return HttpResponse(str(e))


# 编辑客户
def client_edit(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取公司及客户编号
    cli_no = request.GET.get('cli_no')
    try:
        cli_obj = models.Client.objects.filter(no=cli_no, company__user_id=user).first()
        # 获取post请求
        # 获取用户输入数据
        if request.method == 'POST':
            cli_name = request.POST.get('cli_name')
            # 输入为空
            if not cli_name:
                return render(request, 'client_edit.html', {'error': '名称不能为空', 'cli_obj': cli_obj})
            # 输入重复
            elif models.Client.objects.filter(name=cli_name):
                return render(request, 'client_edit.html', {'error': '名称重复', 'cli_obj': cli_obj})
            # 输入有效
            else:
                cli_obj.name = cli_name
                cli_obj.save()
            return redirect('/client_list/')
        else:
            return render(request, 'client_edit.html', {'cli_obj': cli_obj})
    except Exception as e:
        return HttpResponse(str(e))


# 欠款表
def debt_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取供应商信息
    cli_no = request.GET.get('cli_no')

    all_debts = models.Debt.objects.filter(client_id=cli_no, company__user_id=user).distinct()
    # 返回页面
    return render(request, 'debt_list.html', {'all_debts': all_debts, })


# 司机列表
def driver_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取司机列表
    all_drivers = models.Driver.objects.filter(user_id=user)
    count = all_drivers.count()
    page = Pagination(request, count)
    return render(request, 'driver_list.html',
                  {'all_drivers': all_drivers[page.start:page.end], 'page_html': page.page_html})


# 编辑司机
def driver_edit(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取公司及客户编号
    dri_no = request.GET.get('dri_no')
    try:
        dri_obj = models.Driver.objects.get(no=dri_no, user_id=user)
        # 获取用户输入数据
        if request.method == 'POST':
            dri_name = request.POST.get('dri_name')
            # 输入为空
            if not dri_name:
                return render(request, 'driver_edit.html', {'error': '名称不能为空', 'dri_obj': dri_obj})
            # 输入重复
            elif models.Driver.objects.filter(name=dri_name):
                return render(request, 'driver_edit.html', {'error': '名称重复', 'dri_obj': dri_obj})
            # 输入有效
            else:
                dri_obj.name = dri_name
                dri_obj.save()
            return redirect('/driver_list/')
        else:
            return render(request, 'driver_edit.html', {'dri_obj': dri_obj})
    except Exception as e:
        return HttpResponse(str(e))


# 司机查询
def driver_search(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取司机列表
    all_drivers = models.Driver.objects.filter(user_id=user)
    all_orders = None
    total_price = None
    page = Pagination(request, 0)
    try:
        select_dict = {}
        select_dict['driver_id'] = request.GET.get('driver_no')
        select_dict['order_date__gte'] = request.GET.get('start')
        select_dict['order_date__lte'] = request.GET.get('end')
        for key in list(select_dict.keys()):
            if not select_dict[key]:
                del select_dict[key]
        all_orders = models.Order.objects.filter(**select_dict)
        total_price = all_orders.aggregate(total=Sum(F('driver_price') * F('number')))['total']
        total_price = round(total_price if total_price else 0, 2)
        s_name = models.Driver.objects.get(
            no=select_dict['driver_id']).name if 'driver_id' in select_dict else ''
        start_cn = (select_dict['order_date__gte'].replace('-', '年', 1).replace('-',
                                                                                '月') + '日---') if 'order_date__gte' in select_dict else ''
        end_cn = ('---' + select_dict['order_date__lte'].replace('-', '年', 1).replace('-',
                                                                                      '月') + '日') if 'order_date__lte' in select_dict else ''
        s_date = start_cn + end_cn
        count = all_orders.count()
        page = Pagination(request, count)
    except Exception as e:
        return HttpResponse(str(e))
    return render(request, 'driver_search.html',
                  {'all_drivers': all_drivers, 'all_orders': all_orders[page.start: page.end],
                   'total_price': total_price, 's_name': s_name,
                   's_date': s_date,
                   'page_html': page.page_html})


# 增加司机
def driver_add(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': None}
    try:
        driver_name = request.POST.get('driver_name')
        if models.Driver.objects.filter(name=driver_name):
            response_dict['status'] = False
            response_dict['msg'] = '已经存在'
        elif not driver_name:
            response_dict['status'] = False
            response_dict['msg'] = '不能为空'
        else:
            models.Driver.objects.create(name=driver_name, user_id=user)
    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 销售列表
def sale_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取司机列表
    all_sales = models.Sale.objects.filter(user_id=user)
    count = all_sales.count()
    page = Pagination(request, count)
    return render(request, 'sale_list.html',
                  {'all_sales': all_sales[page.start:page.end], 'page_html': page.page_html})


# 编辑司机
def sale_edit(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取公司及客户编号
    sale_no = request.GET.get('sale_no')
    try:
        sale_obj = models.Sale.objects.get(no=sale_no, user_id=user)
        # 获取用户输入数据
        if request.method == 'POST':
            sale_name = request.POST.get('sale_name')
            # 输入为空
            if not sale_name:
                return render(request, 'sale_edit.html', {'error': '名称不能为空', 'sale_obj': sale_obj})
            # 输入重复
            elif models.Sale.objects.filter(name=sale_name):
                return render(request, 'sale_edit.html', {'error': '名称重复', 'sale_obj': sale_obj})
            # 输入有效
            else:
                sale_obj.name = sale_name
                sale_obj.save()
            return redirect('/sale_list/')
        else:
            return render(request, 'sale_edit.html', {'sale_obj': sale_obj})
    except Exception as e:
        return HttpResponse(str(e))


# 销售查询
def sale_search(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取销售列表
    all_sales = models.Sale.objects.filter(user=user)
    all_orders = None
    total_price = None
    page = Pagination(request, 0)
    try:
        select_dict = {}
        select_dict['sale_id'] = request.GET.get('sale_no')
        select_dict['order_date__gte'] = request.GET.get('start')
        select_dict['order_date__lte'] = request.GET.get('end')
        for key in list(select_dict.keys()):
            if not select_dict[key]:
                del select_dict[key]
        all_orders = models.Order.objects.filter(~Q(sale_id=None), **select_dict)
        if all_orders:
            total_price = all_orders.aggregate(total=Sum(F('sale_price') * F('number')))['total']
            total_price = round(total_price if total_price else 0, 2)

        s_name = models.Sale.objects.get(
            no=select_dict['sale_id']).name if 'sale_id' in select_dict else ''
        start_cn = (select_dict['order_date__gte'].replace('-', '年', 1).replace('-',
                                                                                '月') + '日---') if 'order_date__gte' in select_dict else ''
        end_cn = ('---' + select_dict['order_date__lte'].replace('-', '年', 1).replace('-',
                                                                                      '月') + '日') if 'order_date__lte' in select_dict else ''
        s_date = start_cn + end_cn
        count = all_orders.count() if all_orders else 0
        page = Pagination(request, count)
    except Exception as e:
        s_name = ''
        s_date = ''

    return render(request, 'sale_search.html',
                  {'all_sales': all_sales, 'all_orders': all_orders[page.start: page.end], 'total_price': total_price,
                   's_name': s_name,
                   's_date': s_date,
                   'page_html': page.page_html})


# 增加销售
def sale_add(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': None}
    try:
        sale_name = request.POST.get('sale_name')
        if models.Sale.objects.filter(name=sale_name):
            response_dict['status'] = False
            response_dict['msg'] = '已经存在'
        elif not sale_name:
            response_dict['status'] = False
            response_dict['msg'] = '不能为空'
        else:
            models.Sale.objects.create(name=sale_name, user_id=user)
    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 订单列表
def order_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 获取该用户对应的要素
    all_drivers = models.Driver.objects.filter(user=user)
    all_companys = models.Company.objects.filter(user=user)
    all_sales = models.Sale.objects.filter(user=user)
    orders = None
    page = Pagination(request, 0)
    select_error = ''
    s_name = ''
    s_date = ''
    url = str(base64.b64encode(request.get_full_path().encode('utf-8')), 'utf-8')
    try:
        # 获取订单
        select_dict = {}
        select_dict['company__user_id'] = user
        select_dict['company_id'] = request.GET.get('com_no')
        select_dict['supplier_id'] = request.GET.get('sup_no')
        select_dict['client_id'] = request.GET.get('cli_no')
        select_dict['driver_id'] = request.GET.get('dri_no')
        select_dict['sale_id'] = request.GET.get('sale_no')
        select_dict['order_date__gte'] = request.GET.get('start')
        select_dict['order_date__lte'] = request.GET.get('end')
        for key in list(select_dict):
            if not select_dict[key]:
                del select_dict[key]
        orders = models.Order.objects.filter(**select_dict).distinct().order_by('-update_date')
        count = orders.count()
        page = Pagination(request, count)
    except Exception as e:
        select_error = str(e)

    return render(request, 'order_list.html',
                  {'all_companys': all_companys, 'all_drivers': all_drivers, 'all_sales': all_sales,
                   'orders': orders[page.start: page.end], 'select_error': select_error, 's_name': s_name,
                   's_date': s_date,
                   'page_html': page.page_html, 'url': url})


# 增加订单
def order_add(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': None}

    try:
        creat_dict = {}
        creat_dict['company_id'] = request.POST.get('com_no')
        creat_dict['order_date'] = request.POST.get('order_date')
        creat_dict['supplier_id'] = request.POST.get('sup_no')
        creat_dict['client_id'] = request.POST.get('cli_no')
        creat_dict['driver_id'] = request.POST.get('dri_no')
        creat_dict['good_id'] = request.POST.get('good_no')
        creat_dict['driver_price'] = round(Decimal(request.POST.get('dri_price')), 2)
        creat_dict['goods_price'] = round(Decimal(request.POST.get('goods_price')), 2)
        creat_dict['number'] = round(Decimal(request.POST.get('number')), 2)
        creat_dict['remark'] = request.POST.get('remark')
        sale_no = request.POST.get('sale_no')
        sale_price = request.POST.get('sale_price')
        # 进价
        total_buying_price = models.Good.objects.get(no=creat_dict['good_id']).buying_price * creat_dict['number']
        # 商品总价
        total_goods_price = creat_dict['goods_price'] * creat_dict['number']
        # 用户和公司是否匹配
        if models.Company.objects.filter(no=creat_dict['company_id'], user_id=user):
            # 是否有销售人员
            if sale_no:
                # 是否输入价格
                if sale_price:
                    # 有销售及佣金
                    sale_price = round(Decimal(sale_price), 2)
                    creat_dict['sale_id'] = sale_no
                    creat_dict['sale_price'] = sale_price
                    with transaction.atomic():
                        # 创建订单
                        models.Order.objects.create(**creat_dict)
                        # 更新客户欠款
                        debt_obj = models.Debt.objects.get(client_id=creat_dict['client_id'],
                                                           company_id=creat_dict['company_id'])
                        debt_obj.debt -= total_goods_price
                        debt_obj.save()

                        # 更新预付款余额
                        adv_obj = models.Advpayment.objects.get(supplier_id=creat_dict['supplier_id'],
                                                                company_id=creat_dict['company_id'])
                        adv_obj.adv_payment -= total_buying_price
                        adv_obj.save()
                else:
                    # 有销售人员，无价格
                    response_dict['status'] = False
                    response_dict['msg'] = '请输入佣金'
            else:
                with transaction.atomic():
                    # 创建订单,无销售人员
                    models.Order.objects.create(**creat_dict)
                    # 更新客户欠款
                    debt_obj = models.Debt.objects.get(client_id=creat_dict['client_id'],
                                                       company_id=creat_dict['company_id'])
                    debt_obj.debt += total_goods_price
                    debt_obj.save()
                    # 更新预付款余额
                    adv_obj = models.Advpayment.objects.get(supplier_id=creat_dict['supplier_id'],
                                                            company_id=creat_dict['company_id'])
                    adv_obj.adv_payment -= total_buying_price
                    adv_obj.save()
        else:
            response_dict['status'] = False
            response_dict['msg'] = '用户有误'
    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 删除订单
def order_del(request):
    # 获取用户
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    order_no = request.GET.get('ord_no')
    try:
        # 获取订单对象
        order_obj = models.Order.objects.filter(no=order_no, company__user_id=user).first()
        total_price = order_obj.number * order_obj.goods_price  # 总售价
        total_buying_price = order_obj.number * order_obj.good.buying_price  # 总进价
        if request.GET.get('url'):
            url = str(base64.b64decode(request.GET.get('url')), 'utf-8')
            print(url)
        with transaction.atomic():
            # 预付款增加
            models.Advpayment.objects.filter(company_id=order_obj.company_id, supplier_id=order_obj.supplier_id).update(
                adv_payment=F('adv_payment') + total_buying_price)
            # 欠款减少
            models.Debt.objects.filter(company_id=order_obj.company_id, client_id=order_obj.client_id).update(
                debt=F('debt') - total_price)
            # 删除订单
            order_obj.delete()
    except Exception as e:
        return HttpResponse(str(e))
    return redirect(url)


# 商品列表
def good_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    # 当前日期
    cur_date = get_date()
    all_goods = models.Good.objects.filter(end_date__gte=cur_date, start_date__lte=cur_date,
                                           supplier__company__user__no=user).distinct()
    return render(request, 'good_list.html', {'all_goods': all_goods})


# 增加商品
class GoodAdd(View):
    def get(self, request):
        # 获取用户ID
        if user_id(request):
            user = user_id(request)
        else:
            return redirect('/login/')
        all_suppliers = models.Supplier.objects.filter(company__user__no=user).distinct()
        return render(request, 'good_add.html', {'all_suppliers': all_suppliers})

    def post(self, request):
        #
        if user_id(request):
            user = user_id(request)
        else:
            return redirect('/login/')
        # 获取数据
        sup_no = request.POST.get('sup_no')
        good_name = request.POST.get('good_name')
        buying_price = request.POST.get('buying_price')
        all_suppliers = models.Supplier.objects.filter(company__user__no=user).distinct()
        error = ''
        try:
            if sup_no and good_name and buying_price:
                if not models.Good.objects.filter(supplier_id=sup_no, name=good_name):
                    models.Good.objects.create(supplier_id=sup_no, name=good_name, buying_price=buying_price,
                                               end_date='2099-12-31')
                else:
                    error = '已经存在'
            else:
                error = '不能为空'
        except Exception as e:
            error = str(e)
        if error:
            return render(request, 'good_add.html', {'error': error, 'all_suppliers': all_suppliers})
        else:
            return redirect('/good_list/')


# 编辑商品
def good_edit(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': 'None'}
    try:
        sup_no = request.POST.get('sup_no')
        good_no = request.POST.get('good_no')
        good_name = request.POST.get('good_name')
        buying_price = request.POST.get('buying_price')
        eff_date = request.POST.get('eff_date')
        good_obj = models.Good.objects.filter(no=good_no, supplier__company__user_id=user).first()
        if models.Good.objects.filter(supplier_id=sup_no, name=good_name, buying_price=buying_price,
                                      end_date='2099-12-31'):
            response_dict['status'] = False
            response_dict['msg'] = '已经存在'
        else:
            with transaction.atomic():
                import datetime
                # 生效时间
                eff_date = datetime.datetime(int(eff_date[0:4]), int(eff_date[5:7]), int(eff_date[8:10]))
                # 失效时间
                exp_date = eff_date - datetime.timedelta(days=1)
                good_obj.end_date = exp_date
                good_obj.save()
                models.Good.objects.create(supplier_id=sup_no, name=good_name, buying_price=buying_price,
                                           start_date=eff_date,
                                           end_date='2099-12-31')
    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 订单详情
def order_detal(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    error = ''
    order_obj = models.Order.objects.filter(no=-1).first()
    try:
        order_no = request.GET.get('order_no')
        order_obj = models.Order.objects.filter(no=order_no, company__user_id=user).first()
    except Exception as e:
        error = str(e)
    return render(request, 'order_detal.html', {'order': order_obj, 'error': error})


# 付款单列表
def payment_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    all_companys = models.Company.objects.filter(user_id=user)
    page = Pagination(request, 0)
    error = ''
    query = {}
    payments = ''
    url = str(base64.b64encode(request.get_full_path().encode('utf-8')), 'utf-8')
    try:
        if request.method == 'GET':
            query['company__user_id'] = user
            query['company_id'] = request.GET.get('com_no')
            query['supplier_id'] = request.GET.get('supplier_id')
            query['payment_date__gte'] = request.GET.get('start')
            query['payment_date__lte'] = request.GET.get('end')
            for key in list(query):
                if not query[key]:
                    del query[key]
            payments = models.Payment.objects.filter(**query).distinct().order_by('-update_date')
            count = payments.count()
            page = Pagination(request, count)
            print(payments)
    except Exception as e:
        error = str(e)
    return render(request, 'payment_list.html',
                  {'payments': payments[page.start:page.end], 'all_companys': all_companys, 'page_html': page.page_html,
                   'select_error': error, 'url': url})


# 创建付款单
def payment_add(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': None}
    try:
        creat_dict = {}
        creat_dict['company_id'] = request.POST.get('com_no')
        creat_dict['payment_date'] = request.POST.get('payment_date')
        creat_dict['supplier_id'] = request.POST.get('sup_no')
        creat_dict['amount'] = round(Decimal(request.POST.get('amount')), 2)
        creat_dict['remark'] = request.POST.get('remark')
        if models.Company.objects.filter(no=creat_dict['company_id'], user_id=user):
            with transaction.atomic():
                # 创建付款单
                models.Payment.objects.create(**creat_dict)
                # 预付款增加
                adv_obj = models.Advpayment.objects.get(company_id=creat_dict['company_id'],
                                                        supplier_id=creat_dict['supplier_id'])
                adv_obj.adv_payment += creat_dict['amount']
                adv_obj.save()
        else:
            response_dict['status'] = False
            response_dict['msg'] = '用户不符'

    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 删除付款单
def payment_del(request):
    # 获取用户
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    pay_no = request.GET.get('pay_no')
    try:
        # 获取付款单对象
        pay_obj = models.Payment.objects.filter(no=pay_no, company__user_id=user).first()
        total_amount = pay_obj.amount
        if request.GET.get('url'):
            url = str(base64.b64decode(request.GET.get('url')), 'utf-8')
        with transaction.atomic():
            # 预付款降低
            models.Advpayment.objects.filter(company_id=pay_obj.company_id, supplier_id=pay_obj.supplier_id).update(
                adv_payment=F('adv_payment') - total_amount)
            # 删除付款单
            pay_obj.delete()
    except Exception as e:
        return HttpResponse(str(e))
    return redirect(url)


# 收款人列表
def receipt_list(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    all_companys = models.Company.objects.filter(user_id=user)
    page = Pagination(request, 0)
    error = ''
    query = {}
    receipts = ''
    url = str(base64.b64encode(request.get_full_path().encode('utf-8')), 'utf-8')
    try:
        if request.method == 'GET':
            query['company__user_id'] = user
            query['company_id'] = request.GET.get('com_no')
            query['client_id'] = request.GET.get('cli_no')
            query['receipt_date__gte'] = request.GET.get('start')
            query['receipt_date__lte'] = request.GET.get('end')
            for key in list(query):
                if not query[key]:
                    del query[key]
            receipts = models.Receipt.objects.filter(**query).distinct().order_by('-update_date')
            count = receipts.count()
            page = Pagination(request, count)
    except Exception as e:
        error = str(e)
    return render(request, 'receipt_list.html',
                  {'receipts': receipts[page.start:page.end], 'all_companys': all_companys, 'page_html': page.page_html,
                   'select_error': error, 'url': url})


# 创建收款单
def receipt_add(request):
    # 获取用户ID
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    response_dict = {'status': True, 'msg': None}
    try:
        creat_dict = {}
        creat_dict['company_id'] = request.POST.get('com_no')
        creat_dict['receipt_date'] = request.POST.get('receipt_date')
        creat_dict['client_id'] = request.POST.get('cli_no')
        creat_dict['amount'] = round(Decimal(request.POST.get('amount')), 2)
        creat_dict['remark'] = request.POST.get('remark')
        if models.Company.objects.filter(no=creat_dict['company_id'], user_id=user):
            with transaction.atomic():
                # 创建收款单
                models.Receipt.objects.create(**creat_dict)
                # 欠款降低
                debt_obj = models.Debt.objects.get(company_id=creat_dict['company_id'],
                                                   client_id=creat_dict['client_id'])
                debt_obj.debt -= creat_dict['amount']
                debt_obj.save()
        else:
            response_dict['status'] = False
            response_dict['msg'] = '用户有误'
    except Exception as e:
        response_dict['status'] = False
        response_dict['msg'] = str(e)
    response_json = json.dumps(response_dict)
    return HttpResponse(response_json)


# 删除收款单
def receipt_del(request):
    # 获取用户
    if user_id(request):
        user = user_id(request)
    else:
        return redirect('/login/')
    rec_no = request.GET.get('rec_no')
    try:
        # 获取收款单对象
        rec_obj = models.Receipt.objects.filter(no=rec_no, company__user_id=user).first()
        total_amount = rec_obj.amount
        if request.GET.get('url'):
            url = str(base64.b64decode(request.GET.get('url')), 'utf-8')
        with transaction.atomic():
            # 欠款增加
            models.Debt.objects.filter(company_id=rec_obj.company_id, client_id=rec_obj.client_id).update(
                debt=F('debt') + total_amount)
            # 删除付款单
            rec_obj.delete()
    except Exception as e:
        return HttpResponse(str(e))
    return redirect(url)


def get_sup(request):
    # 通过公司获取供应商
    com_no = request.GET.get('com_no')
    sups = models.Supplier.objects.filter(company__no=com_no)

    ret = []
    for i in sups:
        ret.append([i.no, i.name])
    ret_json = json.dumps({'sups': ret})
    return HttpResponse(ret_json)


def get_cli(request):
    # 通过公司获取客户
    com_no = request.GET.get('com_no')
    clis = models.Client.objects.filter(company__no=com_no).distinct()
    ret = []
    for i in clis:
        ret.append([i.no, i.name])
    ret_json = json.dumps({'clis': ret})
    return HttpResponse(ret_json)


def get_good(request):
    # 通过公司获取客户
    sup_no = request.GET.get('sup_no')
    order_date = request.GET.get('order_date')
    if not order_date:
        import datetime
        order_date = datetime.date.today().strftime('%Y-%m-%d')
    goods = models.Good.objects.filter(supplier_id=sup_no, start_date__lte=order_date,
                                       end_date__gte=order_date).distinct()
    ret = []
    for i in goods:
        ret.append([i.no, i.name])
    ret_json = json.dumps({'goods': ret})
    return HttpResponse(ret_json)
