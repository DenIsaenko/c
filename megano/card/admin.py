from django.contrib import admin
from .models import Order, Status, PaymentType


admin.site.register(Order)
admin.site.register(Status)
admin.site.register(PaymentType)
