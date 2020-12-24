from django.db import models


# Create your models here.
class User(models.Model):
    # 用户
    no = models.AutoField(primary_key=True, verbose_name='用户编号')
    username = models.CharField(max_length=32, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=32, verbose_name='密码')

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_user'
        verbose_name = '用户'


class Supplier(models.Model):
    # 供应商
    no = models.AutoField(primary_key=True, db_column='supno', verbose_name='供应商编号')
    name = models.CharField(max_length=32, db_column='supname', verbose_name='供应商名称', unique=True)

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_supplier'
        verbose_name = '供应商'


class Company(models.Model):
    # 公司
    no = models.AutoField(primary_key=True, verbose_name='公司编号')
    name = models.CharField(max_length=32, verbose_name='公司名称', unique=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    suppliers = models.ManyToManyField('Supplier')
    clients = models.ManyToManyField('Client')

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_company'
        verbose_name = '公司'


class Advpayment(models.Model):
    # 预付款
    no = models.AutoField(primary_key=True, verbose_name='编号')
    supplier = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    adv_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='预付款余额')

    def __str__(self):
        return '{}-{}'.format(self.supplier, self.company)

    class Meta:
        # table_name
        db_table = 'tb_advpayment'
        verbose_name = '预付款'
        unique_together = ('supplier', 'company')


class Client(models.Model):
    # 客户
    no = models.AutoField(primary_key=True, db_column='clino', verbose_name='客户编号')
    name = models.CharField(max_length=32, db_column='cliname', verbose_name='客户名称', unique=True)

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_client'
        verbose_name = '客户'


class Good(models.Model):
    # 商品
    no = models.AutoField(primary_key=True, db_column='goodno', verbose_name='商品编号')
    name = models.CharField(max_length=32, db_column='goodname', verbose_name='商品名称')
    supplier = models.ForeignKey('Supplier', on_delete=models.DO_NOTHING)
    buying_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='进价')
    start_date = models.DateField(verbose_name='生效时间', default='2020-01-01')
    end_date = models.DateField(verbose_name='失效时间')

    def __str__(self):
        return '{}-{}-{}'.format(self.no, self.supplier.name, self.name)

    class Meta:
        db_table = 'tb_good'
        verbose_name = '商品'


class Debt(models.Model):
    no = models.AutoField(primary_key=True, db_column='debtno', verbose_name='编号')
    debt = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='欠款')
    client = models.ForeignKey('Client', on_delete=models.DO_NOTHING)
    company = models.ForeignKey('Company', on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}-{}'.format(self.client, self.company)

    class Meta:
        # table_name
        db_table = 'tb_debt'
        verbose_name = '欠款'
        unique_together = ('company', 'client')


class Driver(models.Model):
    # 司机
    no = models.AutoField(primary_key=True, db_column='drino', verbose_name='司机编号')
    name = models.CharField(max_length=32, db_column='driname', verbose_name='司机名称', unique=True)
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_driver'
        verbose_name = '司机'


class Sale(models.Model):
    # 销售人员
    no = models.AutoField(primary_key=True, db_column='salno', verbose_name='销售人员编号')
    name = models.CharField(max_length=32, db_column='salname', verbose_name='销售人员名称', unique=True)
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}-{}'.format(self.no, self.name)

    class Meta:
        # table_name
        db_table = 'tb_sale'
        verbose_name = '销售人员'


class Payment(models.Model):
    # 付款单
    no = models.AutoField(primary_key=True, db_column='payno', verbose_name='付款单编号')
    company = models.ForeignKey('Company', on_delete=models.DO_NOTHING)
    supplier = models.ForeignKey('Supplier', on_delete=models.DO_NOTHING)
    payment_date = models.DateField(verbose_name='付款日期')
    update_date = models.DateTimeField(auto_now=True, verbose_name='修改日期')
    amount = models.DecimalField(max_digits=10, db_column='payamount', decimal_places=2, verbose_name='付款金额')
    remark = models.CharField(max_length=255, verbose_name='备注', null=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.payment_date, self.no, self.supplier.name)

    class Meta:
        # table_name
        db_table = 'tb_payment'
        verbose_name = '付款单'


class Receipt(models.Model):
    # 收款单
    no = models.AutoField(primary_key=True, db_column='recno', verbose_name='收款单编号')
    company = models.ForeignKey('Company', on_delete=models.DO_NOTHING)
    client = models.ForeignKey('Client', on_delete=models.DO_NOTHING)
    receipt_date = models.DateField(verbose_name='收款日期')
    update_date = models.DateTimeField(auto_now=True, verbose_name='修改日期')
    amount = models.DecimalField(max_digits=10, db_column='recamount', decimal_places=2, verbose_name='收款金额')
    remark = models.CharField(max_length=255, verbose_name='备注', null=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.rec_date, self.no, self.supplier.name)

    class Meta:
        # table_name
        db_table = 'tb_receipt'
        verbose_name = '收款单'


class Order(models.Model):
    # 订单
    no = models.AutoField(primary_key=True, db_column='ordno', verbose_name='订单编号')
    goods_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='售价')
    number = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='数量')
    sale_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='销售佣金单价', null=True)
    sale = models.ForeignKey('Sale', on_delete=models.DO_NOTHING, null=True)
    driver_price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='运费单价')
    good = models.ForeignKey('Good', on_delete=models.DO_NOTHING)
    driver = models.ForeignKey('Driver', on_delete=models.DO_NOTHING)
    company = models.ForeignKey('Company', on_delete=models.DO_NOTHING)
    supplier = models.ForeignKey('Supplier', on_delete=models.DO_NOTHING)
    client = models.ForeignKey('Client', on_delete=models.DO_NOTHING)
    order_date = models.DateField(verbose_name='订单日期')
    update_date = models.DateTimeField(auto_now=True, verbose_name='修改日期')
    remark = models.CharField(max_length=255, verbose_name='备注', null=True)

    def __str__(self):
        return '{}-{}-{}'.format(self.no, self.order_date, self.client)

    class Meta:
        db_table = 'tb_order'
        verbose_name = '订单'
