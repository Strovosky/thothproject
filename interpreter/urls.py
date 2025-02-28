from django.urls import path
from .views import register, signin, custom_logout

app_name = "interpreter_urls"

urlpatterns = [
    path(route="", view=signin, name="signin"),
    path(route="register/", view=register, name="register"),
    path(route="logout/", view=custom_logout, name="custom_logout")
]