from django.contrib import admin
from app.models import Supplier, Client, Order, Payment, Receipt, Driver, Sale, Company, Good
# Register your models here.
admin.site.register(Company)
admin.site.register(Supplier)
admin.site.register(Client)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Receipt)
admin.site.register(Driver)
admin.site.register(Sale)
admin.site.register(Good)
