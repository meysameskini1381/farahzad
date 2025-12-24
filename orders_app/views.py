from django.shortcuts import render
def order_user(request):

    return render(request,'orders_app/checkout.html')
