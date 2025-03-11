# Here we have all the API urls
from django.urls import path
from .views import last_10_definitions, category_options, individual_word, create_english_word


urlpatterns = [
    path(route="last_10_definitions/", view=last_10_definitions, name="last_10_definitions"),
    path(route="category_options/", view=category_options, name="category_options"),
    path(route="individual_description/", view=individual_word, name="individual_description"),
    path(route="create_english_word/", view=create_english_word, name="create_english_word")
]






