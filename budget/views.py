from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import requests
from api.endpoints import *
from main.views import data_info_setter, call_workday_retriever, set_call_active, set_call_inactive

# Create your views here.

@method_decorator(login_required, name='dispatch')
class BillingClassView(View):
    """
    This view will handle the logic for the billing template.
    """

    def get(self, request, *args, **kwargs):
        time_out = 2
        token = request.COOKIES.get("auth_token")
        if token:
            headers = {"Authorization":f"Token {token}"}
            call, work_day = call_workday_retriever(request, headers, time_out)
            work_month = requests.get(url=retrieve_current_work_month_endpoint + str(work_day["work_month_id"]) + "/", headers=headers, timeout=time_out)
            if work_month.status_code != 200:
                messages.error(request, "There was an error retrieving the current work month. Please try again later.")
            categories_dict = requests.get(url=category_options_endpoint, headers=headers, timeout=time_out).json()
            data_info = data_info_setter(w_d=work_day, c=call, cat_dict=categories_dict)
            data_info["work_month"] = work_month.json() if work_month.status_code == 200 else None
            return render(request, "budget/billing.html", data_info)
        else:
            messages.error(request, "You are not authenticated. Please log in to access this page.")
            return redirect(to="interpreter_urls:signin")
    
    def post(self, request, *args, **kwargs):
        time_out = 2
        headers = {"Authorization":f"Token {request.COOKIES.get('auth_token')}"}
        call, work_day = call_workday_retriever(request, headers, time_out)
        categories_dict = requests.get(url=category_options_endpoint, headers=headers, timeout=time_out).json()
        work_month = requests.get(url=retrieve_current_work_month_endpoint + str(work_day["work_month_id"]) + "/", headers=headers, timeout=time_out)
        if request.POST.get("word_search"):
            return redirect(to="dashboard_urls:word_search", word=request.POST.get("word_search"))
        elif request.POST.get("btn_set_active_call") or request.POST.get("btn_no_call"):
            answer = set_call_active(r=request, h=headers, w_d=work_day, t=time_out)
            if answer["status"] == True:
                call, work_day = answer["call"], answer["work_day"]
        elif request.POST.get("btn_set_inactive_call"):
            # This will make set the current call to active = False and set the call_end = bogota_time
            if call["active"] == True:
                answer = set_call_inactive(r=request, c=call, h=headers, t=2)
                if answer["status"] == True:
                    call, work_day = answer["call"], answer["work_day"]
        data_info = data_info_setter(w_d=work_day, c=call, cat_dict=categories_dict)
        data_info["work_month"] = work_month.json() if work_month.status_code == 200 else None
        return render(request, "budget/billing.html", data_info)




