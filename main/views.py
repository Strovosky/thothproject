from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from interpreter.models import Interpreter
from .models import Category, English, Spanish, Abbreviation, Definition
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from django.core.paginator import Paginator

import requests


# Creat your endpoints here

last_10_definitions_endpoint = "http://localhost:8000/api/last_10_definitions/"
category_options_endpoint = "http://localhost:8000/api/category_options/"
individual_description_endpoint = "http://localhost:8000/api/individual_description/"


# Create your views here.




@login_required
def dashboard(response):
    if response.method == "POST":
        if response.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=response.POST.get("word_search").lower())
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    return render(response, "main/dashboard.html", {"last_10_definitions":last_10_definitions, "categories_dict":categories_dict})

@login_required
def new_word(request):
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
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    return render(request, "main/new_word.html", {"category_object":Category.objects.all(), "category_dict":categories_dict, "last_10_definitions":last_10_definitions})

@login_required
def word_description(response, id_definition: int):
    if response.method == "POST":
        if response.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=response.POST.get("word_search").lower())
    definition = requests.get(url=individual_description_endpoint, params={"id_definition":id_definition}, timeout=2).json()
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    return render(response, "main/word.html", {"definition":definition, "last_10_definitions":last_10_definitions, "categories_dict":categories_dict})

@login_required
def edit_word(response, id_definition: int):
    definition = get_object_or_404(Definition, pk=id_definition)
    if response.method == "POST":
        if response.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=response.POST.get("word_search").lower())
        else:
            if response.POST.get("edit_english"):
                english = English.objects.filter(definition__id=definition.id)
                english.name = str(response.POST.get("edit_english")).lower()
            if response.POST.get("edit_spanish"):
                spanish = Spanish.objects.filter(definition__id=definition.id)
                spanish.name = str(response.POST.get("edit_spanish")).lower()
            if response.POST.get("edit_abbreviation"):
                abbreviation = Abbreviation.objects.filter(definition__id=definition.id)
                abbreviation.name = str(response.POST.get("edit_abbreviation")).upper()
            if response.POST.get("add_abbreviation"):
                try:
                    new_abbreviation = Abbreviation.objects.get(text=str(response.POST.get("add_abbreviation")).upper())
                    definition.abbreviation.add(new_abbreviation)
                except:
                    definition.abbreviation.create(text=str(response.POST.get("add_abbreviation")).upper())
            if response.POST.get("edit_definition"):
                definition.text = str(response.POST.get("edit_definition")).lower()
            if response.POST.get("another_english"):
                definition.english.create(name=str(response.POST.get("another_english")).lower(), creator=response.user)
            if response.POST.get("another_spanish"):
                definition.spanish.create(name=str(response.POST.get("another_spanish")).lower(), creator=response.user)
        return redirect(to="dashboard_urls:word_description", id_definition=definition.id)
    definition = requests.get(url=individual_description_endpoint, params={"id_definition":id_definition}).json()
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    return render(response, "main/edit_word.html", {"definition":definition, "last_10_definitions":last_10_definitions, "category_dict":categories_dict})

@login_required
def word_search(response, word: str):
    if response.method == "POST":
        if response.POST.get("word_search"):
            return HttpResponseRedirect(reverse("dashboard_urls:word_search", args=(str(response.POST.get("word_search")).lower(),)))
    definitions = Definition.objects.filter(Q(english__name__contains=word) | Q(spanish__name__contains=word) | Q(abbreviation__text__contains=word.upper())).distinct()
    pagination = Paginator(definitions, 10)
    page = response.GET.get("page")
    paginated_definitions = pagination.get_page(page)
    last_10_definitions = requests.get(url=last_10_definitions_endpoint, timeout=2).json()
    categories_dict = requests.get(url=category_options_endpoint, timeout=2).json()
    return render(response, "main/word_search.html", {"definitions":paginated_definitions, "word_to_find":word, "categories_dict":categories_dict, "pagination":pagination, "last_10_definitions":last_10_definitions})



