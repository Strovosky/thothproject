from django.urls import path
from .views import dashboard, new_word, word_description, edit_word, word_search

app_name = "dashboard_urls"


urlpatterns = [
    path(route="", view=dashboard, name="dashboard"),
    path(route="new_word/", view=new_word, name="new_word"),
    path(route="word_description/<int:id_definition>", view=word_description, name="word_description"),
    path(route="edit_word/<int:id_definition>", view=edit_word, name="edit_word"),
    path(route="word_search/<str:word>", view=word_search, name="word_search")
]




