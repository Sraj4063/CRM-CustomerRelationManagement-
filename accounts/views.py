from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm

from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .models import * 
from .forms import OrderForm , CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users,admin_only


@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()  
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            messages.success(request,'Account was created for ' + username)
            
            return redirect('login')
    context = {'form':form}
    return render(request,'accounts/register.html',context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')    #we are getting this from login.html name = username
        password = request.POST.get('password')    #we are getting this from login.html name = password
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Username OR Password is incorrect')
    context = {}
    return render(request,'accounts/login.html',context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url = 'login')
@admin_only
# Create your views here.
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    total_customers = customers.count()

    total_orders = orders.count()     # this we are doing to display on our front page
    delivered = orders.filter(status = 'Delivered').count()  # this we are doing to display on our front page
    pending = orders.filter(status = 'Pending').count()       # this we are doing to display on our front page
    context = {'orders': orders, 'customers':customers,'total_orders':total_orders,'delivered':delivered,'pending':pending }
    return render(request,'accounts/dashboard.html',context)


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()     # this we are doing to display on our front page
    delivered = orders.filter(status = 'Delivered').count()  # this we are doing to display on our front page
    pending = orders.filter(status = 'Pending').count()       # this we are doing to display on our front page


    print('ORDERS',orders)
    context = {'orders':orders,'total_orders':total_orders,'delivered':delivered,'pending':pending}
    return render(request, 'accounts/user.html',context)


@login_required(login_url= 'login')
@allowed_users(allowed_roles = ['customer'])
def accountSettings(request):
    customer = request.user.customer
    form = CustomerForm(instance = customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance = customer)
        if form.is_valid():
            form.save()
    context = {'form':form}
    return render(request,'accounts/account_settings.html',context)



@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    return render(request,'accounts/products.html',{'products' : products})


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id = pk_test)  # as of now we have 2 customer ids , id =1 ,2 , 
                                                 #so we need to write 127.0.0.1:8000/customer/1/, this will open up customer data withoug 
                                                 #creating any new webpage, everything happens dynamically
    orders = customer.order_set.all()
    order_count = orders.count()

    myFilter = OrderFilter(request.GET, queryset = orders)
    orders = myFilter.qs   #qs is queryset  

    context = {'customer':customer,'orders':orders,'order_count':order_count,'myFilter':myFilter}
    return render(request,'accounts/customer.html',context)   


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk): 
    OrderFormSet = inlineformset_factory(Customer,Order,fields = ('product','status'),extra = 10) #syntax - parent-child-fiels, 
                                                                                                    #10 is no. of orders
    customer = Customer.objects.get(id=pk)
    formset = OrderFormSet(queryset = Order.objects.none(),instance = customer) #with this there will be no prefilled order name and status
    #form = OrderForm(initial = {'customer':customer})  #this will plce the name of customer automatically in (place order) after clicking
                                                        # in view(create customer on webpage)
    if request.method == 'POST':
        #print('Printing POST',request.POST)
        #form = OrderForm(request.POST)
        formset = OrderFormSet(request.POST, instance = customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')    # just now we added redirect into our upper import just that after this we can go to our home dashboard

    context = {'formset':formset} 
    return render(request, 'accounts/order_form.html',context)    


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id = pk) #this will prefilled the order details like status,produtc
    form = OrderForm(instance = order) # this will hold it 

    if request.method == 'POST':
        form = OrderForm(request.POST,instance = order) #this will give the updated details and 
        if form.is_valid():
            form.save()
            return redirect('/')   # after saving it return to home

    context = {'form':form}
    return render(request,'accounts/order_form.html',context)    


@login_required(login_url = 'login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    order = Order.objects.get(id = pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')

    context= {'item':order}
    #need to add def __str__(self): return self.product.name in our orders model

    return render(request,'accounts/delete.html',context)    