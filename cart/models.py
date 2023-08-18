from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator



# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return self.company_name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    initial_stock = models.PositiveIntegerField(default=0)  # Add initial stock field
    stock = models.PositiveIntegerField(default=0)  # Add remaining stock field
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Update remaining stock when the product is saved or updated
        if not self.id:
            # For a new product, set remaining stock to initial stock
            self.stock = self.initial_stock
        else:
            # For an existing product, calculate remaining stock
            ordered_quantity = self.orderitem_set.aggregate(sum_quantity=models.Sum('quantity'))['sum_quantity'] or 0
            self.stock = self.initial_stock - ordered_quantity
        super(Product, self).save(*args, **kwargs)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"CartItem {self.id}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    razor_pay_order_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return f"Order {self.id}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

    def save(self, *args, **kwargs):
        # Update the seller's stock when an order item is created or updated
        if not self.id:
            # For a new order item (new purchase), deduct the quantity from the seller's stock
            self.product.initial_stock = self.product.initial_stock - self.quantity
            self.product.save()
        else:
            # For an existing order item (update in quantity), handle the stock change accordingly
            original_quantity = OrderItem.objects.get(id=self.id).quantity
            if self.quantity > original_quantity:
                # If quantity increased, reduce the additional quantity from the seller's stock
                diff_quantity = self.quantity - original_quantity
                self.product.initial_stock -= diff_quantity
                self.product.save()
            elif self.quantity < original_quantity:
                # If quantity decreased, add the reduced quantity back to the seller's stock
                diff_quantity = original_quantity - self.quantity
                self.product.initial_stock += diff_quantity
                self.product.save()

        super(OrderItem, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Update the seller's stock when an order item is deleted
        self.product.initial_stock += self.quantity
        self.product.save()
        super(OrderItem, self).delete(*args, **kwargs)



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[
            MinValueValidator(1, message='Rating should not be less than 1.'),
            MaxValueValidator(5, message='Rating should not be greater than 5.')
        ])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"Shipping Address for {self.user.username}"

class AboutUs(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    description = models.TextField()
    brand_logo = models.ImageField(upload_to='brand_logo', default=False)
    
    def __str__(self):
        return self.description