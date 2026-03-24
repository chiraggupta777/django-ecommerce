from django.contrib import admin
from .models import Phone


class PhoneAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'category',
        'price',
        'is_deal',
        'deal_end_time',
        'discount_percent',
        'get_discounted_price',
    )
    list_editable = ('is_deal', 'discount_percent')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'brand')
    readonly_fields = ('slug', 'get_discounted_price')
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'brand', 'category', 'slug')
        }),
        ('Pricing & Discounts', {
            'fields': ('price', 'is_deal', 'deal_end_time', 'discount_percent', 'get_discounted_price'),
            'description': 'Enable deals to apply discount percent to this product.'
        }),
        ('Details', {
            'fields': ('description', 'image')
        }),
    )

    def get_discounted_price(self, obj):
        """Display the calculated discounted price."""
        try:
            return f"₹{obj.discounted_price()}"
        except Exception:
            return "—"

    get_discounted_price.short_description = "Discounted price"


admin.site.register(Phone, PhoneAdmin)