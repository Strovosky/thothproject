from django.urls import path
from budget.views import BillingClassView


app_name = "budget_urls"

urlpatterns = [
    path(route="", view=BillingClassView.as_view(), name="billing")
]










