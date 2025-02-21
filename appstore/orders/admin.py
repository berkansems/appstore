from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('owner', 'app', 'purchase_date')
    search_fields = ('owner__email', 'app__title')
    list_filter = ('purchase_date',)


admin.site.register(Order, OrderAdmin)
