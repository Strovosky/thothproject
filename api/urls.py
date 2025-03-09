# Here we have all the API urls
from django.urls import path
from .views import last_10_definitions, category_options


urlpatterns = [
    path(route="last_10_definitions/", view=last_10_definitions, name="last_10_definitions"),
    path(route="category_options/", view=category_options, name="category_options")
]






