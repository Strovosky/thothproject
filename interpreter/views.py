from django.shortcuts import render, redirect
from .models import Interpreter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .decorators import not_logged_user
import logging
import requests
from api.endpoints import *

from rest_framework.authtoken.models import Token


# Create useful functions here
def set_calls_inactive(r, h, t):
    """
    This method will get all active calls for the current user and set them to inactive.
    """
    active_calls = requests.get(url=retrieve_active_call_endpoint, headers=h, timeout=t) # We get all calls for current user.
    if active_calls.status_code == 200:
        for call in active_calls.json():
            call_inactive = requests.patch(url=set_call_to_inactive_endpoint + str(call["id"]) + "/", headers=h, data={"active":False, "call_end":timezone.localtime(timezone.now())}, timeout=t)
            print(call_inactive.json(), call_inactive.status_code)
            if call_inactive.status_code != 200:
                for value in call_inactive.json().values():
                    messages.add_message(r, messages.ERROR, value)
    else:
        for value in active_calls.json().values():
            messages.add_message(r, messages.ERROR, value)



# Create your views here.

@not_logged_user
def register(request):
    if request.method == "POST":
        if request.POST.get("user_name") and request.POST.get("user_email") and request.POST.get("user_password") and request.POST.get("terms"):
            info_dic = {"name": request.POST.get("user_name"), "email": request.POST.get("user_email")}
            if Interpreter.objects.filter(username=info_dic["name"]).count() == 0 | Interpreter.objects.filter(email=info_dic["email"]).count() == 0:

                new_interpreter = requests.post(url=create_interpreter_endpoint, data={"username":str(info_dic["name"].lower()), "email":str(info_dic["email"]), "password":request.POST.get("user_password"), "is_active":True}, timeout=60, verify=False)

                all_interpreters = requests.get(url=list_all_interpreters_endpoint, timeout=60, verify=False)
                if all_interpreters.status_code == 200:
                    logging.info("We got all interpreters successfully.")
                    print(all_interpreters.json())
                else:
                    logging.error("We could not get all interpreters.")
                    for value in all_interpreters.json().values():
                        messages.error(request, message=f"{value}")

                if new_interpreter.status_code == 201:
                    logging.info("The user was created successfully.")
                    messages.success(request, message=f"User {info_dic['name']} created successfully.")
                    print(new_interpreter.json())
                    return HttpResponseRedirect(reverse('interpreter_urls:signin'))
                else:
                    logging.error("The user was not created successfully.")
                    for value in new_interpreter.json().values():
                        messages.error(request, message=f"{value}")
                    return HttpResponseRedirect(reverse('interpreter_urls:register'))
            else:
                if Interpreter.objects.filter(username=info_dic["name"]).count() != 0:
                    messages.warning(request, message=f"User {info_dic['name']} already exists.")
                elif Interpreter.objects.filter(email=info_dic["email"]).count() != 0:
                    messages.warning(request, message=f"User email {info_dic['email']} already exists.")
    return render(request, "interpreter/register.html", {})

#@not_logged_user
def signin(response):
    time_out = 2
    if response.method == "POST":
        if response.POST.get("user_email") and response.POST.get("user_password"):
            info_dict = {"email": response.POST.get("user_email"), "password": response.POST.get("user_password")}

            token_answer = requests.post(url=authenticate_interpreter, data={"email":info_dict["email"], "password":info_dict["password"]})
            print(token_answer.json())

            if token_answer.status_code == 200:
                interpreter = Interpreter.objects.get(id=token_answer.json()["interpreter_id"])
                login(response, interpreter)
                logging.info("The info provided was correct and we got the user.")
                #return HttpResponseRedirect(reverse("dashboard_urls:dashboard"))
                set_calls_inactive(r=response, h={"Authorization":f"Token {token_answer.json()["token"]}"}, t=time_out)
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
    token = response.COOKIES["auth_token"]
    headers = {"Authorization":f"Token {token}"}
    time_out = 2
    set_calls_inactive(r=response, h=headers, t=time_out)
    token_response = requests.post(url=destroy_token_endpoint, data={"token":token}, timeout=2)
    logout(response)
    response_http = HttpResponseRedirect(reverse("interpreter_urls:signin"))
    response_http.delete_cookie("auth_token")
    return response_http
