from django.db.models import Count, Min, Max, Avg
from django.shortcuts import render, HttpResponseRedirect, redirect
from .models.product import Product
from .models.category import Category
from .models.customer import Customer
from .froms import CreateProductForm, CreateCategoryForm, CustomerForm, LoginForm
from django.contrib import messages
from .models.order import Order
import pandas as pd
import statistics
from sklearn.metrics.pairwise import cosine_similarity
import operator

def orders(request):

    orders_data = Order.objects.all()

    ratings = pd.DataFrame(list(Order.objects.all().values('customer','product','quantity')))
    
    rating_matrix = ratings.pivot_table(index='customer', columns='product', values='quantity')
    rating_matrix = rating_matrix.fillna(0)
    print(rating_matrix)

    def similar_users(customer, matrix, k=3):
        user = matrix[matrix.index == customer]
        other_users = matrix[matrix.index != customer]
        similarities = cosine_similarity(user, other_users)[0].tolist()

        indices = other_users.index.tolist()
        index_similarity = dict(zip(indices, similarities))

        # sort by similarity
        index_similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
        index_similarity_sorted.reverse()
        
        # grab k users off the top
        top_users_similarities = index_similarity_sorted[:k]
        users = [u[0] for u in top_users_similarities]
        
        return users

    current_user = 4
    similarity_user_indices = similar_users(current_user, rating_matrix)
    print(similarity_user_indices)
    
    context = { 'orderss': orders_data}
    return render(request, "orders.html", context)

def admin_page(request):
    if request.method=="POST":
        product_form = CreateProductForm(request.POST, request.FILES or None)
        if product_form.is_valid():
            product_form.save()
            messages.success(request,'Product Has Been Added Successfully')
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        context = {'product_form': create_product_form, 'category_form': create_category_form}
        return render(request, "add_product.html", context)
    else:
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        customers = Customer.objects.all()
        orders = Order.objects.all()
        print(orders)
        context = {'product_form': create_product_form, 'category_form': create_category_form, 
                        'user': customers, 'orders':orders}
        return render(request, "admin_page.html", context)
    
def update_user_type(request, pk):

    customer = Customer.objects.filter(id=pk).update(customer_type='admin')

    create_product_form = CreateProductForm()
    create_category_form = CreateCategoryForm()
    customers = Customer.objects.all()
    
    context = {'product_form': create_product_form, 'category_form': create_category_form, 
                    'user': customers}
    return render(request, "admin_page.html", context)

def update_user_type(request, pk):

    customer = Customer.objects.filter(id=pk).update(customer_type='admin')

    create_product_form = CreateProductForm()
    create_category_form = CreateCategoryForm()
    customers = Customer.objects.all()
    
    context = {'product_form': create_product_form, 'category_form': create_category_form, 
                    'user': customers}
    return render(request, "admin_page.html", context)

def check_out(request):
    if request.method=="POST":
        address = request.POST.get('address')
        phone = request.POST.get('phone_number')
        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.objects.filter(id__in =(list(cart.keys())))
        
        for product in products:
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.product_price,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))
            order.save()
        request.session['cart'] = {}
        return redirect('cart_page')

def cart_page(request):
    ids = list(request.session.get('cart').keys())
    products_in_cart = Product.objects.filter(id__in = ids)
    return render(request, 'cart.html', { 'products_in_cart': products_in_cart})

def logout(request):
    del request.session['customer']
    cart = request.session.get('cart')
    if cart:
        del request.session['cart']
    return redirect('home_page')

def login(request):
    if request.method=="POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['customer_email']
            password = login_form.cleaned_data['customer_password']  
            customer_check = Customer.objects.filter(customer_email=email,customer_password=password)
            if customer_check:
                if Customer.objects.get(customer_email=email).customer_type == "admin":
                    
                    customer = Customer.objects.get(customer_email=email)
                    request.session['customer'] = customer.id     
                    create_product_form = CreateProductForm()
                    create_category_form = CreateCategoryForm()
                    customers = Customer.objects.all()
                    all_products = Product.objects.all()
                    orders = Order.objects.all()
                    context = {'product_form': create_product_form, 'category_form': create_category_form, 
                                    'user': customers, 'products': all_products, 'orders':orders}
                    return render(request, "admin_page.html", context)
                else:
                    customer = Customer.objects.get(customer_email=email)
                    request.session['customer'] = customer.id
                    
                    products = Product.objects.all()
                    categories = Category.objects.all()
                    recommendations_products = []
                    user_order_check = Order.objects.filter(customer=Customer(id=request.session['customer']))
                    if user_order_check:
                        # recommendations for customer who purchased alredy products
                        ratings = pd.DataFrame(list(Order.objects.all().values('customer','product','quantity')))
                        rating_matrix = ratings.pivot_table(index='customer', columns='product', values='quantity')
                        rating_matrix = rating_matrix.fillna(0)
                        print(rating_matrix)

                        def similar_users(customer, matrix, k=1):
                            user = matrix[matrix.index == customer]
                            other_users = matrix[matrix.index != customer]
                            similarities = cosine_similarity(user, other_users)[0].tolist()

                            indices = other_users.index.tolist()
                            index_similarity = dict(zip(indices, similarities))
                            # sort by similarity
                            index_similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
                            index_similarity_sorted.reverse()
                            # grab k users off the top
                            top_users_similarities = index_similarity_sorted[:k]
                            users = [u[0] for u in top_users_similarities]
                            
                            return users
                        print(str(customer.id))
                        current_user = customer.id
                        similar_user_ids = similar_users(current_user, rating_matrix)
                        print(similar_user_ids[0])
                        ids_of_products = Order.objects.values_list('product', flat=True).filter(customer=Customer(id=similar_user_ids[0]))
                        print(ids_of_products)
                        recommendations_products = Product.objects.filter(id__in=ids_of_products)
                    else:
                        if recommendations_products:
                            recommendations_products = recommendations_products
                        else:
                            recommendations_products = Product.objects.all()
                    
                    return render(request, 'home.html', { 'categories': categories, 'products': products, 'recommendations':recommendations_products})
        else:
            login_form = LoginForm()
            context = {'login_form': login_form}
            return render(request, "login.html", context)
    else:
        login_form = LoginForm()
        context = {'login_form': login_form}
        return render(request, "login.html", context)

def signup_page(request):
    if request.method=="POST":
        customer_form = CustomerForm(request.POST or None)
        if customer_form.is_valid():
            customer_form.save()
            messages.success(request,'You has been registered')
        customer_form = CustomerForm()
        context = {'customer_form': customer_form, 'customer_form': customer_form}
        return render(request, "signup_page.html", context)
    else:
        customer_form = CustomerForm()
        context = {'customer_form': customer_form, 'customer_form': customer_form}
        return render(request, "signup_page.html", context)

def home_page(request, category=None):
    if request.method == "POST":
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product]  = quantity-1
                else:
                    cart[product]  = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        curtomer_previouse_record = request.session.get('customer')

        if curtomer_previouse_record:
            customer_id=request.session['customer']
            customer = Customer.objects.get(id=customer_id)
            request.session['customer'] = customer.id
            print("this is being run")
            products = Product.objects.all()
            categories = Category.objects.all()
            
            
            # recommendations for customer who purchased alredy products

            ratings = pd.DataFrame(list(Order.objects.all().values('customer','product','quantity')))
            
            rating_matrix = ratings.pivot_table(index='customer', columns='product', values='quantity')
            rating_matrix = rating_matrix.fillna(0)
            print(rating_matrix)

            def similar_users(customer, matrix, k=1):
                user = matrix[matrix.index == customer]
                other_users = matrix[matrix.index != customer]
                similarities = cosine_similarity(user, other_users)[0].tolist()

                indices = other_users.index.tolist()
                index_similarity = dict(zip(indices, similarities))

                # sort by similarity
                index_similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
                index_similarity_sorted.reverse()
                
                # grab k users off the top
                top_users_similarities = index_similarity_sorted[:k]
                users = [u[0] for u in top_users_similarities]
                
                return users
            print(str(customer.id))
            current_user = customer.id
            similar_user_ids = similar_users(current_user, rating_matrix)
            print(similar_user_ids[0])
            ids_of_products = Order.objects.values_list('product', flat=True).filter(customer=Customer(id=similar_user_ids[0]))
            print(ids_of_products)
            recommendations_products = Product.objects.filter(id__in=ids_of_products)
            if recommendations_products:
                recommendations_products = recommendations_products
            else:
                recommendations_products = Product.objects.all()

            return render(request, 'home.html', { 'categories': categories, 'products': products, 'recommendations':recommendations_products})
        else:
            return redirect('home_page')

    else:
        
        cart = request.session.get('cart')
        if not cart:
            request.session.cart = {}
        
        products = None
        categories = Category.objects.all()
        categoryID = category
        if categoryID:
            product_category = Category.objects.filter(id= categoryID)
            products = Product.objects.filter(product_catagory__in=product_category)
        else:
            mostly_sold_products = Order.objects.values_list('product', flat=True).distinct()
            products = Product.objects.filter(id__in=mostly_sold_products)
         
        
        return render(request, 'home.html', { 'categories': categories, 'products': products})

def add_product(request):
    if request.method=="POST":
        product_form = CreateProductForm(request.POST, request.FILES or None)
        if product_form.is_valid():
            product_form.save()
            messages.success(request,'Product Has Been Added Successfully')
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        context = {'product_form': create_product_form, 'category_form': create_category_form}
        return render(request, "add_product.html", context)

    else:
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        context = {'product_form': create_product_form, 'category_form': create_category_form}
        return render(request, "add_product.html", context)

def add_category(request):
    if request.method=="POST":
        form = CreateCategoryForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request,'Category of Product has been added successfully')
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        context = {'product_form': create_product_form, 'category_form': create_category_form}
        return render(request, "add_product.html", context)

    else:
        create_product_form = CreateProductForm()
        create_category_form = CreateCategoryForm()
        context = {'product_form': create_product_form, 'category_form': create_category_form}
        return render(request, "add_product.html", context)

def delete_product(request, pk):
    
    Product.objects.filter(id=pk).delete()

    create_product_form = CreateProductForm()
    create_category_form = CreateCategoryForm()
    customers = Customer.objects.all()
    products = Product.objects.all()
    
    context = {'product_form': create_product_form, 'category_form': create_category_form, 
                    'user': customers, 'products': products}
    return render(request, "admin_page.html", context)