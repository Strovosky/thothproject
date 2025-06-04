from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from interpreter.models import Interpreter
from .models import Category, English, Spanish, Abbreviation, Definition
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now, localtime

from django.core.paginator import Paginator

import requests

from api.endpoints import *


# Creat your endpoints here

last_10_definitions_endpoint = "http://localhost:8000/api/last_10_definitions/"
category_options_endpoint = "http://localhost:8000/api/category_options/"
individual_description_endpoint = "http://localhost:8000/api/individual_description/"



# Create useful functions here

def call_workday_retriever(request):
    """
    This function will retrive the requests responses for the call, and work_day
    """
    work_day_response = requests.get(url=retrieve_work_day_endpoint + f"{localtime(timezone.now()).date()}" + "/", headers={"Authorization":f"Token {request.COOKIES.get("auth_token")}"}, timeout=2)
    active_call_list_response = requests.get(url=retrieve_active_call_endpoint, headers={"Authorization":f"Token {request.COOKIES.get('auth_token')}"}, timeout=2)

    if work_day_response.status_code != 200:
        for value in work_day_response.json().values():
            messages.error(request, value)
            return None, None
    else:
        w_d = work_day_response.json()
        if active_call_list_response.status_code != 200:
            for value in active_call_list_response.json().values():
                messages.error(request, value)
                return None, None
        else:
            # Si sí hay llamadas hoy, pero todas son inactivas, pasaremos la última llamada inactiva a call.
            if len(active_call_list_response.json()) == 0:
                last_inactive_call_response = requests.get(url=last_inactive_call, headers={"Authorization":f"Token {request.COOKIES.get("auth_token")}"}, timeout=2)
                if last_inactive_call_response.status_code != 200:
                    for value in last_inactive_call_response.json().values():
                        messages.add_message(request, messages.ERROR, value)
                        return None, None
                else:
                    if len(last_inactive_call_response.json()) > 0:
                        c = last_inactive_call_response.json()[-1]
                        return c, w_d
                    # Si las llamadas inactivas tambien son 0, entonces no hay llamadas
                    else:
                        return None, w_d
            else:
                c = active_call_list_response.json()[-1]
                return c, w_d

def data_info_setter(w_d=None, c=None, ten_def=None, cat_dict=None):
    """
    This functions will verify that the endpoints are in 200/201 or else they'll be passed as None
    """
    data_info = {"last_10_definitions":None, "categories_dict":None, "call":None, "work_day":None}
    if w_d != None:
        data_info["work_day"] = w_d
    if c != None:
        data_info["call"] = c
    if ten_def != None:
        data_info["last_10_definitions"] = ten_def
    if cat_dict != None:
        data_info["categories_dict"] = cat_dict

    return data_info




def dashboard(request):
    token = request.COOKIES.get("auth_token")
    headers = {"Authorization":f"Token {token}"}
    if token:
        call, work_day = call_workday_retriever(request) # The values will be passed in the order: call (first), work_day (second)
        if request.method == "POST":
            if request.POST.get("word_search"):
                return redirect(to="dashboard_urls:word_search", word=request.POST.get("word_search").lower())
            elif request.POST.get("btn_set_active_call") or request.POST.get("btn_no_call"):
                # If there isn't a call and there's a work_day, we create a new call
                print("btn was pressed")
                call_response = requests.post(url=create_call_endpoint, headers=headers, data={"active":True, "work_day":work_day["id"], "interpreter":request.user.id}, timeout=2)
                if call_response.status_code != 201:
                    for value in call_response.json().values():
                        messages.error(request, value)
                else:
                    call = call_response.json()
                    print(call)
            elif request.POST.get("btn_set_inactive_call"):
                # This will make set the current call to active = False and set the call_end = bogota_time
                if call["active"] == True:
                    print(f"La llamada esta activa? {call["active"]}")
                    set_call_inactive_response = requests.patch(url=set_call_to_inactive + str(call["id"]) + "/", headers=headers, data={"active":False, "call_end":timezone.now()}, timeout=2)
                    if set_call_inactive_response.status_code != 200:
                        for value in set_call_inactive_response.json().values():
                            messages.error(request, value)
                    else:
                        print(f"La llamada esta activa? {call["active"]}")
                        call = set_call_inactive_response.json()
                        print(call)

        last_10_definitions = requests.get(url=last_10_definitions_endpoint, headers=headers, timeout=2).json()
        categories_dict = requests.get(url=category_options_endpoint, headers=headers, timeout=2).json()

        data_info = data_info_setter(w_d=work_day, c=call, ten_def=last_10_definitions, cat_dict=categories_dict)
        print(type(work_day))

        # Here we make sure, if we have an active call, we use it, else we provide whatever value "call" had.
        the_render = render(request, "main/dashboard.html", data_info)
        the_render.set_cookie("auth_token", token, httponly=True)
        return the_render
    else:
        return HttpResponseRedirect(reverse("interpreter_urls:signin"))

@login_required
def new_word(request):
    """
    This view will render the template for creating a new word.
    """
    call, work_day = call_workday_retriever(request)

    if request.method == "POST":
        if request.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=request.POST.get("word_search").lower())
        elif request.POST.get("english") and request.POST.get("spanish") and request.POST.get("definition") and request.POST.get("category"):
            dict_info = {
                "english": str(request.POST.get("english")).lower(),
                "spanish": str(request.POST.get("spanish")).lower(),
                "definition": str(request.POST.get("definition")).lower(),
                "category": str(request.POST.get("category")).lower()
            }
            
            try:
                word_result = Definition.objects.filter(Q(english__name=dict_info["english"]) | Q(spanish__name=dict_info["spanish"]) & Q(category__name=dict_info["category"]))
            except:
                messages.error(request, message=f"The word {dict_info['english']} / {dict_info['spanish']} already exists in the dictionary.")
            else:
                if word_result.count() == 0:
                    english = English.objects.create(name=str(dict_info["english"]).lower())
                    english.save()
                    spanish = Spanish.objects.create(name=str(dict_info["spanish"]).lower())
                    spanish.save()
                    category = Category.objects.get(name=str(dict_info["category"]).lower())
                    definition = Definition.objects.create(text=str(dict_info["definition"]).lower(), category=category)
                    definition.save()
                    definition.english.add(english)
                    definition.spanish.add(spanish)
                    if request.POST.get("abbreviation"):
                        if Abbreviation.objects.filter(text=str(request.POST.get("abbreviation")).upper()).count() > 0:
                            abbreviation = Abbreviation.objects.get(text=str(request.POST.get("abbreviation")).upper())
                        else:
                            abbreviation = Abbreviation.objects.create(text=str(request.POST.get("abbreviation")).upper())
                            abbreviation.save()
                        definition.abbreviation.add(abbreviation)
                    
                    return redirect(to="dashboard_urls:word_description", id_definition=definition.id)
                else:
                    messages.error(request, message=f"The word {dict_info['english']} / {dict_info['spanish']} already exists in the dictionary.")
        else:
            messages.error(request, "The required fields must be filled to create a new word.")
    token = request.COOKIES["auth_token"]
    headers = {"Authorization":f"Token {token}"}
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, headers=headers, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()

    data_info = data_info_setter(w_d=work_day, c=call, ten_def=last_10_definitions, cat_dict=categories_dict)
    data_info["category_object"] = Category.objects.all()

    return render(request, "main/new_word.html", data_info)

@login_required
def word_description(response, id_definition: int):
    """
    This function will render the template that shows a specific word description
    """
    call, work_day = call_workday_retriever(response)
    if response.method == "POST":
        if response.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=response.POST.get("word_search").lower())
    token = response.COOKIES["auth_token"]
    headers = {"Authorization":f"Token {token}"}
    definition = requests.get(url=individual_description_endpoint, headers=headers, params={"id_definition":id_definition}, timeout=2).json()
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, headers=headers, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    info_dict = data_info_setter(w_d=work_day, c=call, ten_def=last_10_definitions, cat_dict=categories_dict)
    info_dict["definition"] = definition
    return render(response, "main/word.html", info_dict)

@login_required
def edit_word(response, id_definition: int):
    """
    This view will render the template for editing a word.
    """
    call, work_day = call_workday_retriever(response)
    definition = get_object_or_404(Definition, pk=id_definition)
    if response.method == "POST":
        if response.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=response.POST.get("word_search").lower())
        else:
            if response.POST.get("btn_change_english"):
                english = English.objects.get(name=response.POST.get("btn_change_english"))
                english.name = str(response.POST.get("edit_english")).lower()
                english.save()
            if response.POST.get("btn_change_spanish"):
                spanish = Spanish.objects.get(name=response.POST.get("btn_change_spanish"))
                spanish.name = str(response.POST.get("edit_spanish")).lower()
                spanish.save()
            if response.POST.get("edit_abbreviation"):
                abbreviation = Abbreviation.objects.filter(definition__id=definition.id)
                abbreviation.name = str(response.POST.get("edit_abbreviation")).upper()
            if response.POST.get("add_abbreviation") and response.POST.get("btn_add_abbreviation") == "pressed":
                try:
                    new_abbreviation = Abbreviation.objects.get(text=str(response.POST.get("add_abbreviation")).upper())
                    definition.abbreviation.add(new_abbreviation)
                except:
                    definition.abbreviation.create(text=str(response.POST.get("add_abbreviation")).upper())
            if response.POST.get("change_definition") and response.POST.get("btn_change_definition") == "pressed":
                definition.text = str(response.POST.get("change_definition")).lower()
                definition.save()
            if response.POST.get("another_english") and response.POST.get("btn_add_english") == "pressed":
                definition.english.create(name=str(response.POST.get("another_english")).lower(), creator=response.user)
            if response.POST.get("another_spanish") and response.POST.get("btn_add_spanish") == "pressed":
                definition.spanish.create(name=str(response.POST.get("another_spanish")).lower(), creator=response.user)
        return redirect(to="dashboard_urls:word_description", id_definition=definition.id)
    token = response.COOKIES.get("auth_token")
    headers = {"Authorization":f"Token {token}"}
    definition = requests.get(url=individual_description_endpoint, headers=headers, params={"id_definition":id_definition}).json()
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, headers=headers, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    info_dict = data_info_setter(w_d=work_day, c=call, ten_def=last_10_definitions, cat_dict=categories_dict)
    info_dict["definition"] = definition
    return render(response, "main/edit_word.html", info_dict)

@login_required
def word_search(response, word: str):
    call, work_day = call_workday_retriever(response)
    if response.method == "POST":
        if response.POST.get("word_search"):
            return HttpResponseRedirect(reverse("dashboard_urls:word_search", args=(str(response.POST.get("word_search")).lower(),)))

    definitions = Definition.objects.filter(Q(english__name__contains=word) | Q(spanish__name__contains=word) | Q(abbreviation__text__contains=word.upper())).distinct()
    pagination = Paginator(definitions, 10)
    page = response.GET.get("page")
    paginated_definitions = pagination.get_page(page)

    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()

    data_info = data_info_setter(w_d=work_day, c=call, ten_def=last_10_definitions, cat_dict=categories_dict)
    data_info["word_to_find"] = word
    data_info["definitions"] = paginated_definitions
    data_info["pagination"] = pagination

    return render(response, "main/word_search.html", data_info)



