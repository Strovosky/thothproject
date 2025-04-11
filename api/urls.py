# Here we have all the API urls
from django.urls import path
from .views import last_10_definitions, category_options, individual_word, create_english_word, CreateInterpreterAPIView, RetrieveUpdateDestroyInterpreterAPIView, AuthenticateInterpreterAPIView, DestroyCurrentToken

urlpatterns = [
    path(route="last_10_definitions/", view=last_10_definitions, name="last_10_definitions"),
    path(route="category_options/", view=category_options, name="category_options"),
    path(route="individual_description/", view=individual_word, name="individual_description"),
    path(route="create_english_word/", view=create_english_word, name="create_english_word"),
    path(route="create_interpreter/", view=CreateInterpreterAPIView.as_view(), name="create_interpreter"),
    path(route="retrive_update_destroy_interpreter/<int:pk>/", view=RetrieveUpdateDestroyInterpreterAPIView.as_view(), name="retrive_update_destroy_interpreter"),
    path(route="auth_interpreter/", view=AuthenticateInterpreterAPIView.as_view(), name="auth_interpreter"),
    path(route="destroy_token/", view=DestroyCurrentToken.as_view(), name="destroy_token")
]






