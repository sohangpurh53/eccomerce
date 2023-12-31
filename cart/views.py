from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, OrderItem, Product, Category,Seller, Cart, CartItem, ShippingAddress,Review, AboutUs, ProductImage
from .forms import ContactForm, SellerRegistrationForm, ProductForm, SignupForm,LoginForm, ShippingAddressForm, ReviewForm, AboutUsForm, ProductImageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# Create your views here.

#homepage display all product
def Homepage(request):
    products = Product.objects.all()

    product_data = []
    for product in products:
        # Retrieve a single image for each product
        try:
            product_image = ProductImage.objects.filter(product=product).first()
            image_url = product_image.image.url if product_image else None
        except ProductImage.DoesNotExist:
            image_url = None

        product_data.append({
            'product': product,
            'image_url': image_url,
        })
    
    sort = request.GET.get('sort', 'name')  # Default sorting by product name
    if sort == 'name':
        products = Product.objects.order_by('name')
    elif sort == 'price_low':
        products = Product.objects.order_by('price')
    elif sort == 'price_high':
        products = Product.objects.order_by('-price')
    return render(request, 'homepage.html', {'product_data': product_data,  'sort':sort})


#display single product and review
def productpage(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    
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
    return render(request, 'product.html', {'product':product, 'reviews':reviews, 'form':form, 'user_has_reviewed': user_has_reviewed, 'product_images':product_images})



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
            shipping_fee = request.POST.get('shipping_fee')
            initial_stock = request.POST.get('initial_stock')
            stock = request.POST.get('stock')
            category_id = request.POST.get('product_category')
            
            
            category = Category.objects.get(id=category_id)
            seller = request.user.seller
            
            Product.objects.create(name=name, description=description, price=price, shipping_fee=shipping_fee, initial_stock=initial_stock, stock=stock,
                                   category=category, seller=seller)
             
            
        
            
            return redirect('seller_dashboard')
           
   
    # Retrieve products and categories for the current seller
    
    seller = request.user.seller
    products = Product.objects.filter(seller=seller)
    categories = Category.objects.all()
    product_data = []
    for product in products:
        # Retrieve a single image for each product
        try:
            product_image = ProductImage.objects.filter(product=product).first()
            image_url = product_image.image.url if product_image else None
        except ProductImage.DoesNotExist:
            image_url = None

        product_data.append({
            'product': product,
            'image_url': image_url,
        })
        
    
    
   

    context = {
        'products': products,
        'categories': categories,
        'product_data': product_data,
        
     
        
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
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {'form': form, 'product': product}

    return render(request, 'seller_editproduct.html', context)


def product_image(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            product_image = ProductImage(product=product, image=image)
            product_image.save()
            messages.success(request, 'Product image added successfully.')
            return redirect('product_image', product_id=product_id)
    else:
        form = ProductImageForm()

    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'product_image.html', context)
    

#categories page 
def categories_product(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    product_data = []
    for product in products:
        # Retrieve a single image for each product
        try:
            product_image = ProductImage.objects.filter(product=product).first()
            image_url = product_image.image.url if product_image else None
        except ProductImage.DoesNotExist:
            image_url = None

        product_data.append({
            'product': product,
            'image_url': image_url,
        })
        
        product_detail = product_data
        


    
    context = {
        'categories': categories,
        'products': products,
        'product_detail':product_detail,
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
    
    # Calculate the subtotal and total shipping fees
    subtotal = 0
    total_shipping_fee = 0
    for item in cart_items:
        item_total_price = item.product.price * item.quantity
        subtotal += item_total_price
        total_shipping_fee += item.product.shipping_fee * item.quantity
    
    # Calculate the total amount including shipping fees
    total_amount = subtotal + total_shipping_fee
    cart_item_data = []
    for item in cart_items:
        product_image = ProductImage.objects.filter(product=item.product).first()
        cart_item_data.append({
            'cart_item': item,
            'product_image': product_image
        })

    context = {
        'cart': cart,
        'cart_item_data':cart_item_data,
        'subtotal': subtotal,
        'shipping_fee': total_shipping_fee,
        'total_amount': total_amount,
        
       
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
    old_shipping_addresses = ShippingAddress.objects.filter(user=request.user)
    created_at = request.POST.get('created_at')
    
    
    if request.method == 'POST':
        address_choice = request.POST.get('address_choice')

        if address_choice == 'new':
            # Retrieve new address data from the form
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            country = request.POST.get('country')
            postal_code = request.POST.get('postal_code')

            # Create a new ShippingAddress instance
            if address==address and city==city and state==state and country==country and postal_code==postal_code:
             shipping_address = ShippingAddress.objects.get_or_create(
                user=user,
                address=address,
                city=city,
                state=state,
                country=country,
                postal_code=postal_code
            )
             
        else:
            # Retrieve the selected saved address
            chosen_address = ShippingAddress.objects.get(id=int(address_choice))
            shipping_address = chosen_address
            print(shipping_address)
        # Calculate total amount, create order, and save order items
        subtotal = 0
        total_shipping_fee = 0
        for item in cart_items:
            item_total_price = item.product.price * item.quantity
            subtotal += item_total_price
            total_shipping_fee += item.product.shipping_fee * item.quantity
        total_amount = subtotal + total_shipping_fee

        

        
        
        # Razorpay payment integration
        client = razorpay.Client(auth=(settings.KEY_ID, settings.KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': int(total_amount * 100),
            'currency': 'INR',
            'payment_capture': 1,
        })
        order = Order.objects.create(
                    user=user, created_at=created_at, total_amount=total_amount, razor_pay_order_id=razorpay_order['id']
                )
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )

        
           
        context = {
            'razorpay_key': settings.KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            
        }
        return render(request, 'checkout.html', context)
    cart_item_data = []
    for item in cart_items:
        product_image = ProductImage.objects.filter(product=item.product).first()
        cart_item_data.append({
            'cart_item': item,
            'product_image': product_image
        })

    subtotal = 0
    total_shipping_fee = 0
    for item in cart_items:
            item_total_price = item.product.price * item.quantity
            subtotal += item_total_price
            total_shipping_fee += item.product.shipping_fee * item.quantity
    total_amount = subtotal + total_shipping_fee
    context = {
        'cart_items': cart_item_data,
        'old_shipping_addresses': old_shipping_addresses,
       'total_amount':total_amount,
       'shipping_fee':total_shipping_fee,
        
        
    }
    return render(request, 'checkout.html', context)


#order success page
@login_required(login_url='signin')
def payment_success(request):
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    payment_signature = request.GET.get('razorpay_signature')
    shipping_address = request.GET.get('shipping_address')
    print(shipping_address)
    
    order = Order.objects.get(razor_pay_order_id=order_id)
    
    
    user_shipping_address = ShippingAddress.objects.filter(user=request.user).latest('id')
            
            # Create the shipping address string
    shipping_address = (
                f"{user_shipping_address.address}, "
                f"{user_shipping_address.city}, "
                f"{user_shipping_address.state}, "
                f"{user_shipping_address.country}, "
                f"{user_shipping_address.postal_code}"
            )
    
    
    # Check if the email has already been sent for this order in the session
    if not request.session.get('order_email_sent_{}'.format(order.id), False):
        # Save payment information in your Order model
        order.razor_pay_payment_id = payment_id
        order.razor_pay_payment_signature = payment_signature
        order.is_paid = True  # Update the order status
        order.shipping_address = shipping_address
        order.save()

        # Retrieve order items for the email template
        order_items = OrderItem.objects.filter(order=order)


        email_context = {
        'user': request.user,
        'order_items': order_items,
        'order': order,
        'request': request,  # Pass the request object
    }

        # Send an order confirmation email to the user
        subject = 'Order Confirmation'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email]
        html_message = render_to_string('orderconfirmationemail.html', {'user': request.user, 'order_items': order_items, 'order': order})
        send_mail(subject, '', from_email, recipient_list, fail_silently=False, html_message=html_message)

        # Send order confirmation email to sellers
        for sellerorder in order_items:
            seller_subject = 'New Order Received'
            seller_from_email = settings.EMAIL_HOST_USER  
            seller_recipient_list = [sellerorder.product.seller.user.email]  
            seller_html_message = render_to_string('sellerorderconfirmation.html', {'seller': sellerorder.product.seller, 'order_items': order_items, 'order': order})
            send_mail(seller_subject, '', seller_from_email, seller_recipient_list, fail_silently=False, html_message=seller_html_message)

        # Mark that the email has been sent for this order in the session
        request.session['order_email_sent_{}'.format(order.id)] = True
    
    # Clear cart items if the order is paid
    if order.is_paid:
        cart_items = CartItem.objects.all()
        cart_items.delete()
        
        
    
    return render(request, 'success.html', {'payment_id': payment_id, 'order_id': order_id})


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
    shipping_address = ShippingAddress.objects.filter(user=user)
    
    count = shipping_address.count()
    
    
    order_data = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        order_data.append({
            'order': order,
            'order_items': order_items
        })

    context = {'user':user, 'order_data': order_data, 'shipping_address':shipping_address, 'count':count}
          
    return render(request, 'userprofile.html', context)





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



# changes in about us page/edit aboutus 
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



#display aboutus
def about_us(request):
    # Retrieve the AboutUs instance for the logged-in seller
    about_us = AboutUs.objects.last()   
    return render(request, 'about_us.html', {'about_us': about_us})





#display single order detail
@login_required(login_url='signin')
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # shipping_address = ShippingAddress.objects.get(user=order.shippping_address)  # Assuming each user has a single shipping address
    
    context = {
        'order': order,
        # 'shipping_address': shipping_address,
    }
    
    return render(request, 'order_details.html', context)



#edit shipping address
@login_required(login_url='signin')
def shipping_address_edit(request, shipping_address_id):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    form = ShippingAddressForm
    if request.method=='POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address Updated Successfully')
            return redirect('userprofile')
    else:
        form = ShippingAddressForm(instance=shipping_address)

    context =  {'form':form}
    return render(request, 'shipping_address_edit.html',context)



#create new shipping address
# @login_required(login_url='signin')
# def create_shipping_address(request):
#       old_shipping_addresses = ShippingAddress.objects.filter(user=request.user)

#       if old_shipping_addresses:
#           messages.success(request, 'Same Address Already Exist')
#       if request.method=='POST':
#            user = request.user  # Assuming you're using Django's built-in User model
#            address = request.POST.get('address')
#            city = request.POST.get('city')
#            state = request.POST.get('state')
#            country = request.POST.get('country')
#            postal_code = request.POST.get('postal_code')  # Get the address data from the form

#         # Create a new shipping address record associated with the user
#            ShippingAddress.objects.get_or_create(user=user, address=address, city=city, state=state, country=country, postal_code=postal_code)
#            return redirect('userprofile')
   
#       return render(request, 'form_shipping_address.html')
        


#  current not in use
@login_required(login_url='signin')
def shipping_address_delete(request, shipping_address_id):
    shipping_address = get_object_or_404(ShippingAddress, id=shipping_address_id)
    shipping_address.delete()
    messages.success(request, 'Address deleted successfully')
    return redirect('userprofile')





# Contact us form
@login_required(login_url='signin')
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            # Send email to the designated recipient
            recipient_email = settings.EMAIL_HOST_USER  # Replace with actual email
            recipient_message = render_to_string('recipient_contact_email.html', {
                'user': request.user,
                'subject': subject,  # Add subject to context
                'message': message,
                'sender': sender,
            })
            send_mail(subject, strip_tags(recipient_message), sender, [recipient_email], html_message=recipient_message)

            company = 'Lulu-Collection53'
            user_message = render_to_string('user_thank_you_email.html', {
                'user': request.user,
                'company': company
            })
            # Send a confirmation email to the user
            send_mail('Thank you for contacting us', strip_tags(user_message), recipient_email, [sender], html_message=user_message)

            return redirect('thankyou')  # Create this template
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form})
      

def thankyou(request):
    return render(request, 'thank_you_for_contact.html')

  