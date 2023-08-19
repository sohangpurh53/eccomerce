from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderItem, Product, Category,Seller, Cart, CartItem, ShippingAddress,Review, AboutUs
from .forms import SellerRegistrationForm, ProductForm, SignupForm,LoginForm, ShippingAddressForm, ReviewForm, AboutUsForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

#homepage display all product
def Homepage(request):
    products = Product.objects.all()
    sort = request.GET.get('sort', 'name')  # Default sorting by product name
    if sort == 'name':
        products = Product.objects.order_by('name')
    elif sort == 'price_low':
        products = Product.objects.order_by('price')
    elif sort == 'price_high':
        products = Product.objects.order_by('-price')
    return render(request, 'homepage.html', {'products':products, 'sort':sort})


#display single product and review
def productpage(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    user_has_reviewed = False  # Flag to track if the current user has already reviewed the product

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if the user has already reviewed the product
            user_review = Review.objects.filter(product=product, user=request.user).first()
            if user_review:
                # User has already reviewed the product, handle the case (e.g., show message)
                user_has_reviewed = True
            else:
                # User has not reviewed the product, save the review
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                return redirect('productpage', product_id=product_id)
       
    else:
            form = ReviewForm()    
    return render(request, 'product.html', {'product':product, 'reviews':reviews, 'form':form, 'user_has_reviewed': user_has_reviewed})



#seller dashboard create and update products
@login_required(login_url='seller_login')
def seller_dashboard(request):
    if request.method == 'POST':
        # Create Category
        if 'create_category' in request.POST:
            name = request.POST.get('category_name')
            Category.objects.create(name=name)
            return redirect('seller_dashboard')
        
        # Add Product
        elif 'add_product' in request.POST:
            name = request.POST.get('product_name')
            description = request.POST.get('product_description')
            price = request.POST.get('product_price')
            initial_stock = request.POST.get('initial_stock')
            category_id = request.POST.get('product_category')
            image = request.FILES.get('product_image')
            
            category = Category.objects.get(id=category_id)
            seller = request.user.seller
            
            Product.objects.create(name=name, description=description, price=price, initial_stock=initial_stock,
                                   category=category, seller=seller, image=image)
            return redirect('seller_dashboard')

    # Retrieve products and categories for the current seller
    seller = request.user.seller
    products = Product.objects.filter(seller=seller)
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'seller_dashboard.html', context)



#seller (new seller registraion)
def seller_registration(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_seller = True
            user.save()
            company_name = form.cleaned_data.get('company_name')
            Seller.objects.create(user=user, company_name=company_name)
            return redirect('seller_dashboard')  # Redirect to the login page after successful registration
    else:
        form = SellerRegistrationForm()
    return render(request, 'seller_registration.html', {'form': form})


#seller (authentication)
def seller_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        
        if user is not None and user.is_authenticated:
            try:
                seller = user.seller  # Access the seller object associated with the user
                login(request, user)
                messages.success(request, 'Login Successfully')
                return redirect('seller_dashboard')
            except Seller.DoesNotExist:
                error_message = "You are not authorized as a seller."
                return render(request, 'seller_login.html', {'error_message': error_message})
        else:
            messages.success(request, ("Invalid login credentials."))
        
        return redirect('seller_dashboard')  # Redirect to the seller dashboard after successful login
    
    return render(request, 'seller_login.html')




#seller (poduct edit page)
@login_required(login_url='seller_login')
def seller_editproduct(request, product_id):
    products = get_object_or_404(Product, id=product_id)

    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=products)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
            
    else:
        form = ProductForm(instance=products)
        return render(request, 'seller_editproduct.html', {'form':form})
    

#categories page 
def categories_product(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'categories.html', context)



#cartpage
@login_required(login_url='signin')
def cart_view(request):
    try:
        # Get the user's cart
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
    except Cart.DoesNotExist:
        # If the cart does not exist, create a new one
        cart = Cart.objects.create(user=request.user)
        cart_items = []
    
    # Calculate the subtotal
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    # Calculate the total amount including shipping fees
    shipping_fee = 50
    if subtotal > 599:
        shipping_fee = 0  # Free shipping
    total_amount = subtotal + shipping_fee

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total_amount': total_amount
    }


    return render(request, 'cart.html', context)



#new user creation
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signin')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


#user authentication Signin page
def signin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('Homepage')  # Replace 'home' with your desired URL name
    else:
        form = LoginForm()
    return render(request, 'signin.html', {'form': form})

#Signout user 
def signout(request):
    logout(request)
    messages.success(request, ('Logout Succesfully'))
    return redirect('Homepage')


#add quantity cart items
@login_required(login_url='signin')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

        if item_created:
            # Item added to the cart successfully
            messages.success(request, 'Item added to cart.')
        else:
            cart_item.quantity += 1  # Increase the quantity by 1
            cart_item.save()
            messages.success(request, 'Item quantity updated.')
            return redirect('cart_view')

        if request.GET.get('buy_now') == 'true':
            return redirect('checkout')
        else:
            return redirect('productpage', product_id=product_id)

    else:
        # User is not authenticated
        return JsonResponse({'message': 'User is not authenticated.'})
    

 #remove quantity cart items
@login_required(login_url='signin')
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    cart_item.delete()
    messages.success(request, ('Cart Item Removed'))
    # Optionally, you can update the cart count or perform any other necessary actions
    
    return redirect('cart_view')


#reduce quantity cart items
@login_required(login_url='signin')
def reduce_quantity(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(request, ('Item quantity updated.'))
    else:
        cart_item.delete()
        messages.success(request, ('Cart item removed.'))
    
    return redirect('cart_view')




#checkout page
@login_required(login_url='signin')
def checkout(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    
    
    

    shipping_fee = 0
    total_amount = sum(item.product.price * item.quantity + shipping_fee for item in cart_items)

    if total_amount <= 599:
        shipping_fee = 50
        total_amount = sum(item.product.price * item.quantity + shipping_fee for item in cart_items)

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        created_at = request.POST.get('created_at')
        

        shipping_address = ShippingAddress.objects.create(
            user=user,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code
        )

        client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(total_amount * 100),
            'currency': 'INR',
            'payment_capture': 1,
        })
       
        order = Order(user=user, created_at=created_at, total_amount=total_amount, razor_pay_order_id=razorpay_order['id'])
        order.save()

        

        

        # Save order items and update product stocks
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
            # Update the product's initial stock
            

            #empty cart item after order
            

        

        context = {
            'cart_items': cart_items,
            'cart_total': total_amount,
            'shipping_fee': shipping_fee,
            'currency': 'INR',
            'razorpay_key': settings.KEY_ID,
            'razorpay_order_id': razorpay_order['id'],

        }

        # Redirect to Razorpay payment page
        return render(request, 'checkout.html', context)

    return render(request, 'checkout.html', {'cart_items': cart_items})


#order success page
@login_required(login_url='signin')
def payment_success(request):
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    payment_signature = request.GET.get('razorpay_signature')
    
    

    # Save payment information in your Order model
    order = Order.objects.get(razor_pay_order_id=order_id)
    order.razor_pay_payment_id = payment_id
    order.razor_pay_payment_signature = payment_signature
    order.is_paid = True  # Update the order status
    order.save()

    if order.is_paid == True:
     cart_item = CartItem.objects.all()
     cart_item.delete()
    order = Order.objects.get(razor_pay_order_id=order_id)

    return render(request, 'success.html', {'payment_id':payment_id, 'order_id':order_id})


#order failure page
def payment_failure(request):
    error_code = request.GET.get('error_code')
    error_description = request.GET.get('error_description')

    return render(request, 'failedpayment.html', {'error_code': error_code, 'error_description': error_description})




#seller profile page
@login_required(login_url='seller_login')
def sellerprofile(request):
   seller = Seller.objects.get(user=request.user)

    # Get all the products for the seller
   products = Product.objects.filter(seller=seller)

    # Get the remaining stock for each product
   for product in products:
        product.remaining_stock = product.stock - sum(item.quantity for item in product.orderitem_set.all())

    # Get the orders that include the seller's products
   orders = OrderItem.objects.filter(product__seller=seller).order_by('-order__created_at')

   context = {
        'seller': seller,
        'products': products,
        'orders': orders,
    }

   return render(request, 'sellerprofile.html', context)



#userprofile page
@login_required(login_url='signin')
def userprofile(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    
    order_data = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        order_data.append({
            'order': order,
            'order_items': order_items
        })

    
          
    return render(request, 'userprofile.html', {'user':user, 'order_data': order_data})





#review edit page 
def edit_review(request, product_id, review_id):
    review = get_object_or_404(Review, id=review_id, product_id=product_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('productpage', product_id=product_id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'edit_review.html', {'form': form})




@login_required(login_url='seller_login')
def edit_about_us(request):
    # Check if the user is a seller
    if not request.user.seller:
        # Redirect to a page with an appropriate message or raise an exception
        return redirect('seller_login')

    about_us, created = AboutUs.objects.get_or_create(seller=request.user.seller)

    if request.method == 'POST':
        description = request.POST.get('description')
        brand_logo = request.FILES.get('brand_logo') 
        about_us.description = description
        about_us.brand_logo = brand_logo
        about_us.save()
        return redirect('Homepage')

    return render(request, 'edit_about_us.html', {'about_us': about_us})


def about_us(request):
    # Retrieve the AboutUs instance for the logged-in seller
    about_us = AboutUs.objects.last()   
    return render(request, 'about_us.html', {'about_us': about_us})

