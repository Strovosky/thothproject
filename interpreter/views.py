from django.shortcuts import render, redirect
from .models import Interpreter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .decorators import not_logged_user
import logging


# Create your views here.

@not_logged_user
def register(response):
    if response.method == "POST":
        if response.POST.get("user_name") and response.POST.get("user_email") and response.POST.get("user_password") and response.POST.get("terms"):
            info_dic = {"name": response.POST.get("user_name"), "email": response.POST.get("user_email")}
            if Interpreter.objects.filter(username=info_dic["name"]).count() | Interpreter.objects.filter(email=info_dic["email"]).count() == 0:
                new_interpreter = Interpreter.objects.create(
                    username = str(info_dic["name"]).lower(),
                    email = info_dic["email"]
                )
                new_interpreter.set_password(response.POST.get("user_password"))
                new_interpreter.save()
                return HttpResponseRedirect(reverse('interpreter_urls:signin'))
            else:
                if Interpreter.objects.filter(username=info_dic["name"]).count() != 0:
                    messages.warning(response, message=f"User {info_dic['name']} already exists.")
                elif Interpreter.objects.filter(email=info_dic["email"]).count() != 0:
                    messages.warning(response, message=f"User email {info_dic['email']} already exists.")
    return render(response, "interpreter/register.html", {})

@not_logged_user
def signin(response):
    if response.method == "POST":
        if response.POST.get("user_email") and response.POST.get("user_password"):
            info_dict = {"email": response.POST.get("user_email"), "password": response.POST.get("user_password")}

            user = authenticate(response, username=info_dict["email"], password=info_dict["password"])

            if user is not None:
                login(response, user)
                logging.info("The info provided was correct and we got the user.")
                return HttpResponseRedirect(reverse("dashboard_urls:dashboard"))            
            else:
                logging.error("The email or username are incorrect")
                messages.error(response, message=f"The email or password is incorrect.")
                return HttpResponseRedirect(reverse("interpreter_urls:signin"))
        else:
            logging.error("The info added wasn't valid.")
            messages.error(response, message=f"You must input an email and password.")
            return HttpResponseRedirect(reverse("interpreter_urls:signin"))

    return render(response, "interpreter/sign-in.html", {})

@login_required
def custom_logout(response):
    logout(response)
    return HttpResponseRedirect(reverse("interpreter_urls:signin"))
