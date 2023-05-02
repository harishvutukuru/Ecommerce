from django.db import models
from django.contrib.auth.models import User


# Create your models here.


# CATEGORY = (
#     ('Clothes', 'Clothes'),
#     ('Electronics', 'Electronics'),
#     ('Home Appliances', 'Home Appliances'),
# )
class UserProfile(User):
    user_type = (
        ('customer', 'customer'),
        ('staff', 'staff'),
        ('vendor', 'vendor'),
    )
    user_role = models.CharField(
        max_length=20, choices=user_type, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    quantity = models.IntegerField(default=0)
    cost_per_item = models.DecimalField(
        max_digits=19, decimal_places=2, null=False, blank=False)
    product_image = models.ImageField(upload_to="media/", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    order_status_track = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Dispatched", "Dispatched"),
        ("Received", "Received")
    )
    name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(default=0)
    order_status = models.CharField(
        max_length=20, choices=order_status_track, blank=True, null=True
    )
    amount = models.FloatField(default=0, blank=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True)
    order_details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0, )
    price = models.DecimalField(
        max_digits=19, decimal_places=2, null=False, blank=False)
    total_amount = models.DecimalField(
        max_digits=19, decimal_places=2, null=False, blank=False)
    sale_date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100, null=False, blank=False)
    customer_mobile = models.CharField(max_length=100, null=False, blank=False)
    customer_address = models.TextField()


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=19, decimal_places=2, null=False, blank=False)
    total_amount = models.DecimalField(
        max_digits=19, decimal_places=2, null=False, blank=False)
    purchase_date = models.DateTimeField(auto_now_add=True)
    vendor = models.ForeignKey(UserProfile, on_delete=models.CASCADE)


class ecom(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null=True)
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True)
    pur_qty = models.PositiveIntegerField(default=0)
    sale_qty = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    total_qty = models.PositiveIntegerField(null=True)
