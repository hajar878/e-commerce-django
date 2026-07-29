from django.shortcuts import render , redirect
from django.views import View
from . models import Product , Customer, Cart,OrderPlaced,Wishlist
from django.db.models import Count
from . forms import CustomerRegistrationForm , CustomerProfileForm 
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Wishlist


# Create your views here.
def home(request):
    return render(request,"app/home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title =Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
class CategoryTitle(View):
    def get(self,request,val):
        product= Product.objects.filter(title=val)
        title =Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())



class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())

class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html',locals())   
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Congratulations! User Register Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/customerregistration.html',locals()) 

class ProfileView(View):
    def get(self,request):
        form= CustomerProfileForm()
        return render(request,"app/profile.html",locals())
    def post(self,request):
        form= CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']

            reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city)
            reg.save()
            messages.success (request, "Congratulations! Profile Save Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return render(request,"app/profile.html",locals())
    
def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request,"app/address.html",locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request,"app/updateAddress.html",locals())

    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.save()
            messages.success (request, "Congratulations! Profile Update Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")   

def add_to_cart(request):
    user=request.user
    product_id=request.GET.get( 'prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save() 
    return redirect("/cart")  

def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.selling_price
        amount = amount + value
    totalamount = amount + 40    
    return render(request, 'app/addtocart.html',locals())


def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        cart = Cart.objects.filter(user=request.user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.selling_price

        totalamount = amount + 40  # frais de livraison

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }

        return JsonResponse(data)
    
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
        if c.quantity > 1:
            c.quantity -= 1
            c.save()

        cart = Cart.objects.filter(user=request.user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.selling_price

        totalamount = amount + 40

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        }

        return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = get_object_or_404(Cart, Q(product=prod_id) & Q(user=request.user))
        c.delete()

        cart = Cart.objects.filter(user=request.user)
        amount = 0
        for p in cart:
            amount += p.quantity * p.product.selling_price

        totalamount = amount + 40 if amount > 0 else 0

        data = {
            'amount': amount,
            'totalamount': totalamount
        }

        return JsonResponse(data)    

@login_required
def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    amount = 0
    for item in cart_items:
        amount += item.quantity * item.product.selling_price
    totalamount = amount + 40  # Livraison

    if request.method == 'POST':
        for item in cart_items:
            OrderPlaced.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                ordered_date=datetime.now()
            )
        cart_items.delete()  # vider le panier après la commande
        return redirect('orders')  # page de confirmation ou historique

    return render(request, 'app/checkout.html', {'cart_items': cart_items, 'amount': amount, 'totalamount': totalamount})        


@login_required
def add_to_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        product = get_object_or_404(Product, id=prod_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return JsonResponse({'message': 'Produit ajouté à la wishlist'})

@login_required
def remove_from_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        product = get_object_or_404(Product, id=prod_id)
        Wishlist.objects.filter(user=request.user, product=product).delete()
        return JsonResponse({'message': 'Produit retiré de la wishlist'})
    
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'app/wishlist.html', {'wishlist_items': wishlist_items})

