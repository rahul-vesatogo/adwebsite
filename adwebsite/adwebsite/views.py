# Import necessary modules and models
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
from .query import get_products
import requests

def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/home/')
    return render(request, 'registration/login.html')

@login_required
def custom_logout(request):
    logout(request)
    return redirect('/login/')

@login_required
def home(request):
    username = request.user.username
    url = "http://127.0.0.1:8000/graphql"
    product = get_products()
    grapql_request = requests.post(url=url, json={"query": product}) 
    return render(request, 'home.html', {'username': username, 'products': product})
