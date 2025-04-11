from django.shortcuts import render, redirect
from .models import Interpreter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .decorators import not_logged_user
import logging
import requests
from api.endpoints import create_interpreter_endpoint, authenticate_interpreter, destroy_token_endpoint

from rest_framework.authtoken.models import Token

# Create your views here.

@not_logged_user
def register(request):
    if request.method == "POST":
        if request.POST.get("user_name") and request.POST.get("user_email") and request.POST.get("user_password") and request.POST.get("terms"):
            info_dic = {"name": request.POST.get("user_name"), "email": request.POST.get("user_email")}
            if Interpreter.objects.filter(username=info_dic["name"]).count() == 0 | Interpreter.objects.filter(email=info_dic["email"]).count() == 0:
                #new_interpreter = Interpreter.objects.create(
                #    username = str(info_dic["name"]).lower(),
                #    email = info_dic["email"]
                #)
                new_interpreter = requests.post(url=create_interpreter_endpoint, data={"username":str(info_dic["name"].lower()), "email":str(info_dic["email"]), "password":request.POST.get("user_password")})
                #new_interpreter.set_password(response.POST.get("user_password"))
                #new_interpreter.save()
                return HttpResponseRedirect(reverse('interpreter_urls:signin'))
            else:
                if Interpreter.objects.filter(username=info_dic["name"]).count() != 0:
                    messages.warning(request, message=f"User {info_dic['name']} already exists.")
                elif Interpreter.objects.filter(email=info_dic["email"]).count() != 0:
                    messages.warning(request, message=f"User email {info_dic['email']} already exists.")
    return render(request, "interpreter/register.html", {})

#@not_logged_user
def signin(response):
    try:
        auth_token_key = response.COOKIES["auth_token"]
        response = HttpResponseRedirect(reverse("dashboard_urls:dashboard"))
        response.set_cookie("auth_token", auth_token_key, httponly=True)
        return response
    except:
        if response.method == "POST":
            if response.POST.get("user_email") and response.POST.get("user_password"):
                info_dict = {"email": response.POST.get("user_email"), "password": response.POST.get("user_password")}

                token_answer = requests.post(url=authenticate_interpreter, data={"email":info_dict["email"], "password":info_dict["password"]})

                if token_answer.status_code == 200:
                    interpreter = Interpreter.objects.get(id=token_answer.json()["interpreter_id"])
                    login(response, interpreter)
                    logging.info("The info provided was correct and we got the user.")
                    #return HttpResponseRedirect(reverse("dashboard_urls:dashboard"))
                    response = HttpResponseRedirect(reverse("dashboard_urls:dashboard"))
                    response.set_cookie("auth_token", token_answer.cookies["auth_token"], httponly=True)
                    return response
                else:
                    logging.error("The email or username are incorrect")
                    messages.error(response, message=f"The email or password is incorrect.")
                    return HttpResponseRedirect(reverse("interpreter_urls:signin"))
            else:
                logging.error("The info added wasn't valid.")
                messages.error(response, message=f"You must input an email and password.")
                return HttpResponseRedirect(reverse("interpreter_urls:signin"))
        return render(response, "interpreter/sign-in.html", {})

#@login_required
def custom_logout(response):
    token_response = requests.post(url=destroy_token_endpoint, data={"token":response.COOKIES["auth_token"]}, timeout=2)
    logout(response)
    response_http = HttpResponseRedirect(reverse("interpreter_urls:signin"))
    response_http.delete_cookie("auth_token")
    return response_http
