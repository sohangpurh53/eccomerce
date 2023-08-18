from django.contrib import admin
from .models import Cart ,Category, Order, Product, ShippingAddress, Seller, Review, OrderItem, CartItem, AboutUs
# Register your models here. 
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(ShippingAddress)
admin.site.register(Seller)
admin.site.register(Review)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(AboutUs)
