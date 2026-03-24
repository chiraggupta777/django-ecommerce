from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User


class Phone(models.Model):
    CATEGORY_MOBILE = 'mobile'
    CATEGORY_ACCESSORY = 'accessory'
    CATEGORY_EARBUDS = 'earbuds'
    CATEGORY_CHARGER = 'charger'

    CATEGORY_CHOICES = [
        (CATEGORY_MOBILE, 'Mobile'),
        (CATEGORY_ACCESSORY, 'Accessory'),
        (CATEGORY_EARBUDS, 'Earbuds'),
        (CATEGORY_CHARGER, 'Charger'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.IntegerField()
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_MOBILE,
    )
    image = models.ImageField(upload_to='phones/')
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    discount_percent = models.IntegerField(default=0, help_text="Discount percentage (0-100%)")

    # Deals let you apply a discount to an existing product record.
    is_deal = models.BooleanField(default=False)
    deal_end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            index = 1
            while Phone.objects.filter(slug=slug).exists():
                slug = f"{base}-{index}"
                index += 1
            self.slug = slug

        # Validate discount only when this product is marked as a deal.
        if self.is_deal:
            if self.discount_percent < 0 or self.discount_percent > 100:
                raise ValidationError("Discount percent must be between 0 and 100.")

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    def discounted_price(self):
        """
        Return the discounted price when this product is a deal.
        Otherwise, return the original price.
        """
        if not self.is_deal:
            return self.price

        # Price is stored as an integer, so we return an integer after discount.
        return (self.price * (100 - self.discount_percent)) // 100


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.IntegerField(default=0)
    address = models.TextField(default="", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"Order #{self.id} - {self.get_status_display()}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Phone, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantity}× {self.product.name} (Order #{self.order.id})"
