from django.urls import path
from .views import *

urlpatterns=[
    path('contactus/',contact),
    path('register/',register),
    path('verify/<auth_token>',verify),
    path('login/',login)

]