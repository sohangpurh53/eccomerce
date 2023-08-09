from django.contrib import admin
from django.urls import path, include
from cart import views

urlpatterns = [
    path('', views.Homepage, name='Homepage' ),
    path('product/<int:product_id>/', views.productpage, name='productpage'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/register/', views.seller_registration, name='seller_registration'),
    path('seller/login/', views.seller_login, name='seller_login'),
     path('seller/product/<int:product_id>/edit/', views.seller_editproduct, name='seller_editproduct'),
     path('category/', views.categories_product, name='categories_product'),
     path('cart/', views.cart_view, name='cart_view'),
     path('signup/', views.signup, name='signup'),
     path('signin/', views.signin, name='signin'),
     path('signout/', views.signout, name='signout'),
     path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
     path('cart/<int:cart_item_id>/delete/', views.remove_cart_item, name='remove_cart_item'),
     path('cart/<int:cart_item_id>/', views.reduce_quantity, name='reduce_quantity'),
     path('checkout/', views.checkout, name='checkout'),
     path('order-success/', views.order_success, name='order_success'),
     path('sellerprofile/', views.sellerprofile, name='sellerprofile'),
     path('userprofile/', views.userprofile, name='userprofile'),
     path('paymentfail/', views.paymentfail, name='paymentfail'),
    path('product/<int:product_id>/edit_review/<int:review_id>/', views.edit_review, name='edit_review'),
    
 
    
  
    
   
    

]