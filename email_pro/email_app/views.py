import uuid

from django.shortcuts import render,redirect
from .forms import *
from django.core.mail import send_mail
from email_pro.settings import EMAIL_HOST_USER
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth import authenticate
from django.http import HttpResponse



# Create your views here.
def contact(request):
    sub=ContactusForm()
    if request.method=='POST':
        sub=ContactusForm(request.POST)
        if sub.is_valid():
            email=sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message=sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message,EMAIL_HOST_USER, [email],fail_silently=False)
            return render(request,'contactussuccess.html')
    return render(request,'contactus.html',{'form':sub})


def register(request):
    if request.method=='POST':
        username=request.POST.get('username')           # .get --> to get username value directly from html page --> amal
        email=request.POST.get('email')
        password=request.POST.get('password')
        #checking whether the username & email provided already exists.
        if User.objects.filter(username=username).first():          # checking amal already exists in User
            messages.success(request,'username already taken')
            return redirect(register)
        if User.objects.filter(email=email).first():
            messages.success(request,'email already exist')
            return redirect(register)
        user_obj=User(username=username,email=email)
        user_obj.set_password(password)
        user_obj.save()         # saved to UserModel
        auth_token=str(uuid.uuid4())
        profile_obj=profile.objects.create(user=user_obj,auth_token=auth_token)
        profile_obj.save()          # model saved
        send_mail_register(email,auth_token)        # to send mail
        return render(request,'contactussuccess.html')
    return render(request,'register.html')


def send_mail_register(email,token):
    subject="Your Account has been Verified"
    message=f'paste the link to verify your account http://127.0.0.1:8000/email_app/verify/{token}'
    email_from=EMAIL_HOST_USER
    recipient=[email]
    send_mail(subject,message,email_from,recipient)

def verify(request,auth_token):
    profile_obj=profile.objects.filter(auth_token=auth_token).first()
    if profile_obj:
        if profile_obj.is_verified:
            messages.success(request,'Your account is already verified')
            return redirect(login)
        profile_obj.is_verified=True
        profile_obj.save()
        messages.success(request,'Your account has been verified')
        return redirect(login)
    else:
        return HttpResponse("Error")


def login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user_obj=User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request,'user not found')
            return redirect(login)
        profile_obj=profile.objects.filter(user=user_obj).first()
        if not profile_obj.is_verified:
            messages.success(request,'profile not Verified. Check Your mail')
            return redirect(login)
        user=authenticate(username=username,password=password)
        if user is None:
            messages.success(request,'Wrong Password or username')
            return redirect(login)
        return HttpResponse("Success")
    return render(request,'login.html')
