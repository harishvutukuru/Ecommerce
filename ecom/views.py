from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count, Sum,Value,F, CharField,ExpressionWrapper,Case,When,OuterRef,Subquery,Exists
import datetime
from django.contrib.auth import authenticate, login
from django.db.models.functions import Concat

# Create your views here.


def index(request):
    if request.user.userprofile.user_role=='customer':
        exists = cart.objects.filter(product_id=OuterRef('id'),user=request.user)
        product = Product.objects.annotate(image=ExpressionWrapper(
            Concat(Value('http://localhost:8000/media/'), F('product_image')),
            output_field=CharField()),is_added_cart=Exists(exists)).all()
        context = {'role': request.user.userprofile.user_role,
                   'product': product
                   }
        return render(request, "ecom/ecom_customer.html",context)
    else:
        return render(request, "ecom/index.html")


def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            # user = UserProfile.objects.filter(username=username, password=password)
            user = authenticate(
                request=request, username=username, password=password
            )
            if user:
                login(request, user)
                context ={'role': user.userprofile.user_role}
                if user.userprofile.user_role == 'customer':
                    return index(request)
                else:
                    return render(request, "ecom/index.html", context)
            else:
                messages.error(request, "Invalid login credentials")
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            messages.error(request, 'Error in login')
            return redirect('login')
    else:
        form = UserLoginForm()
    context = {
        'form': form
    }
    return render(request, "ecom_system/login.html", context)


def product(request):
    product = Product.objects.annotate(image=ExpressionWrapper(
    Concat(Value('http://localhost:8000/media/'), F('product_image')),
    output_field=CharField())).all()
    product_count = product.count()
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # set the product_image attribute to the uploaded file
            product.product_image = request.FILES['product_image']
            # save the product instance to the database
            product.save()
            # form.save()
            #ecom.objects.create(product=form.instance,pur_qty = form.cleaned_data.get('quantity'))
            product_name = form.cleaned_data.get('name')
            messages.success(request, f'{product_name} has been added')
            return redirect('product')
        else:
            messages.error(request, 'Error in product creation')
            return redirect('product')
    else:
        print(product.values())
        form = ProductForm()
    context = {
        'product': product,
        'form': form,
        'product_count': product_count,
        'role':UserProfile.objects.get(id=request.user.id).user_role
    }
    return render(request, "ecom/product.html", context)


def product_edit(request, pk):
    item = Product.objects.get(id=pk)
    print(request.method)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=item)
        if form.is_valid():
            product = form.save(commit=False)
            # set the product_image attribute to the uploaded file
            product.product_image = request.FILES['product_image']
            # save the product instance to the database
            product.save()
            #inst = ecom.objects.get(product=form.instance, purchase_id=None,sale_id=None)
            #inst.pur_qty = inst.pur_qty + int(form.cleaned_data.get('quantity'))
            #inst.save()
            return redirect('product')
    else:
        form = ProductForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'ecom/product_edit.html', context)


def product_delete(request, pk):
    item = Product.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('product')
    context = {
        'item': item
    }
    return render(request, 'ecom/product_delete.html', context)


def order(request):
    if request.user.userprofile.user_role=='staff' or request.user.is_superuser:
        order = Order.objects.all()
    else:
        order = Order.objects.filter(user=request.user)
    order_count = order.count()
    product = Product.objects.all()
    product_count = product.count()

    context = {
        'order': order,
        'product_count': product_count,
        'order_count': order_count,
        'user': UserProfile.objects.get(id=request.user.id)
    }
    return render(request, 'ecom/order.html', context)


def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            qty = form.cleaned_data.get('order_quantity')
            if qty == 0 or qty < 0:
                messages.error(request, 'Quantity can not be less than or equal to 0 ')
                return render(request, 'ecom/product_detail.html', {})
            elif product.quantity >= qty:
                product.quantity -= qty
            else:
                messages.error(request, 'Quantity can not be greater than to the available products')
                return render(request, 'ecom/product_detail.html', {})
            product.save()
            ecom.objects.create(product=product,sale_qty =qty)
             
            Order.objects.filter(id=form.instance.id).update(user_id=request.user.id, order_status='Pending', amount=product.cost_per_item*int(qty))
            return redirect('order')
    else:
        form = OrderForm(instance=product)
    context = {
        'product': product,
        'form': form
    }
    return render(request, 'ecom/product_detail.html', context)


def purchase(request):
    purchase = Purchase.objects.all()
    purchase_count = purchase.count()
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            product = form.cleaned_data.get('product')
            prod_inst = Product.objects.get(id=product.id)
            prod_inst.quantity = prod_inst.quantity + form.cleaned_data.get('qty')
            prod_inst.save()
            inst, created = ecom.objects.get_or_create(product=product, purchase=form.instance)
            if created:
                inst.pur_qty = form.cleaned_data.get('qty')
            else:
                inst.pur_qty = inst.pur_qty + form.cleaned_data.get('qty')
            inst.save()
            messages.success(request, f'purchased successfully')
            return redirect('purchase')
        else:
            messages.error(request, 'Error in purchase creation')
            return redirect('purchase')
    else:
        form = PurchaseForm()
    context = {
        'purchase': purchase,
        'form': form,
        'purchase_count': purchase_count,
    }
    return render(request, "ecom/purchase.html", context)


def sale(request):
    sale = Sale.objects.all()
    sale_count = sale.count()
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data.get('product')
            prod = Product.objects.get(id=product.id)
            quantity = prod.quantity - form.cleaned_data.get('qty')
            if quantity >= 0:
                form.save()
            else:
                messages.error(request, f'Products are not available in this quantities')
                return redirect('sale')
            prod.quantity = quantity
            prod.save()
            inst, created = ecom.objects.get_or_create(product=product, sale=form.instance)
            if created:
                inst.sale_qty = form.cleaned_data.get('qty')
            else:
                inst.sale_qty = inst.sale_qty + form.cleaned_data.get('qty')
            inst.save()

            messages.success(request, f'sold successfully')
            return redirect('sale')
        else:
            messages.error(request, 'Error in sell')
            return redirect('sale')
    else:
        form = SaleForm()
    context = {
        'sale': sale,
        'form': form,
        'sale_count': sale_count,
    }
    return render(request, "ecom/sale.html", context)


def user_create(request):
    user = UserProfile.objects.all()
    user_count = user.count()
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'User is created successfully')
            return redirect('user_create')
        else:
            messages.error(request, 'Error in user creation')
            return redirect('user_create')
    else:
        form = UserForm()
    context = {
        'users': user,
        'user': request.user,
        'form': form,
        'user_count': user_count,
    }
    return render(request, "ecom/user_create.html", context)


def user_edit(request, pk):
    item = UserProfile.objects.get(id=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('user_create')
    else:
        form = UserForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'ecom/user_edit.html', context)


def user_delete(request, pk):
    item = User.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('user_create')
    context = {
        'item': item
    }
    return render(request, 'ecom/user_delete.html', context)


def user(request):
    users = list(User.objects.values('first_name', 'email', 'username'))
    context = {'users': users}
    return render(request, "ecom/user.html", context)


def ecom(request):
    sales = ecom.objects.values('product').annotate(total_qty=Sum('pur_qty') - Sum('sale_qty')).order_by().values('product__name', 'total_qty')
    out_of_stock_products = []
    product_in_loss = []
    for i in sales:
        if i['total_qty'] < 1:
            out_of_stock_products.append(i)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    most_purchased_product = ecom.objects.filter(date__date=today).values('product').annotate(
        total_qty=Sum('pur_qty')).order_by('-total_qty').values('product__name', 'total_qty', 'product__cost_per_item').first()
    try:
        most_sold_product = ecom.objects.filter(date__date=today).values('product').annotate(total_qty=Sum('sale_qty')).order_by('total_qty').values('product__name', 'total_qty', 'product__cost_per_item')[0]
    except:
        most_sold_product = {}
    products_price = ecom.objects.values('product').annotate(total_sale=Sum('sale_qty') ).order_by().values(
       'product_id', 'product__name', 'total_sale')

    for i in products_price:
        try:
           total_price = Sale.objects.filter(product_id=i['product_id']).aggregate(ta=Sum('total_amount',default=0))['ta'] - Product.objects.filter(id=i['product_id'])[0].cost_per_item*i['total_sale']
           if total_price < 0:
               product_in_loss.append({'product__name': i['product__name'],'total_price':total_price})
        except:
            pass

    context = {
        'most_purchased_product': most_purchased_product,
        'most_sold_product': most_sold_product,
        'product_out_of_stocks': out_of_stock_products,
        'product_in_loss': product_in_loss
    }

    return render(request, "ecom/ecom.html", context)


def stats(request):
    staffs = UserProfile.objects.filter(user_role='customer').count()
    vendors = UserProfile.objects.filter(user_role='vendor').count()
    products = Product.objects.count()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    count_sell = ecom.objects.filter(date__date=today).aggregate(
        total_qty_sum=Sum('sale_qty'))
    total_product_sold = ecom.objects.values('product').annotate(
        total_product=Sum('pur_qty') - Sum('sale_qty')).order_by().filter(total_product__lte=0).count()

    total = 0
    if count_sell:
        total = count_sell['total_qty_sum']
    context = {'staffs': staffs,
               'orders': total,
               'products': products,
               'vendors': vendors,
               'remaining_product': products-total_product_sold}
    return render(request, "ecom/stats.html", context)


def category(request):
    inst = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'{name} has been created')
            return redirect('category')
        else:
            messages.error(request, 'Error in category creation')
            return redirect('category')
    else:
        form = CategoryForm()
    context = {
        'category': inst,
        'form': form,
    }
    return render(request, "ecom/category.html", context)


def category_edit(request, pk):
    item = Category.objects.get(id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('category')
    else:
        form = CategoryForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'ecom/category_edit.html', context)


def category_delete(request, pk):
    item = Category.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('category')
    context = {
        'item': item
    }
    return render(request, 'ecom/category_delete.html', context)


def sub_category(request):
    inst = SubCategory.objects.all()
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'{name} has been created')
            return redirect('sub_category')
        else:
            messages.error(request, 'Error in Sub Category creation')
            return redirect('sub_category')
    else:
        form = SubCategoryForm()
    context = {
        'sub_category': inst,
        'form': form,
    }
    return render(request, "ecom/sub_category.html", context)


def sub_category_edit(request, pk):
    item = SubCategory.objects.get(id=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('sub_category')
    else:
        form = SubCategoryForm(instance=item)
    context = {
        'form': form,
    }
    return render(request, 'ecom/sub_category_edit.html', context)


def sub_category_delete(request, pk):
    item = SubCategory.objects.get(id=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('sub_category')
    context = {
        'item': item
    }
    return render(request, 'ecom/sub_category_delete.html', context)


def settings(request):
    return render(request, 'ecom/settings.html', {})

def order_status_update(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        form = OrderFormStatus(request.POST,instance=order)
        if form.is_valid():
            form.save()
            return redirect('order')
    else:
        form = OrderFormStatus(instance=order)
    context = {
        'form': form
    }
    return render(request, 'ecom/order_status_update.html', context)

def AccessDeniend(request):
    return render(request, 'ecom/access_denied.html', {})

def cart_view(request):
    context = {'cart_items':cart.objects.filter(user=request.user).annotate(image=ExpressionWrapper(
    Concat(Value('http://localhost:8000/media/'), F('product__product_image')),
    output_field=CharField())).all()}
    return render(request, 'ecom/cart_checkout.html', context)

def checkout(request):
     return render(request, 'ecom/access_denied.html', context)

def AddCart(request,pk=None):
    if request.method == 'GET' and pk is not None:
        instance, created = cart.objects.get_or_create(product_id=pk,user_id=request.user.id,quantity=1)
        if created:
            pass
        else:
            instance.quantity = instance.quantity+1
        instance.save()

        messages.success(request, f'{instance.product.name} has been added to the cart')
        
    return index(request)


def UpdateCart(request,pk=None):
    if pk is not None:
        cart_ins = cart.objects.get(id=pk)
        if request.method == 'POST':
            cart_ins.quantity = request.POST.get('quantity')
            cart_ins.save()
    
    return cart_view(request)

def RemoveCart(request,pk=None):
    if pk is not None:
        cart_ins = cart.objects.get(id=pk)
        if request.method == 'POST':
            cart_ins.delete()
       
    return cart_view(request)