# Here we'll store all of the endpoints


#base_url = "http://localhost:8000/api/"
base_url = "https://thothproject-production-8ffe.up.railway.app/api/"


# Interpreter endpoints
list_all_interpreters_endpoint = base_url + "list_all_interpreters/"
authenticate_interpreter = base_url + "auth_interpreter/"
destroy_token_endpoint = base_url + "destroy_token/"
create_interpreter_endpoint = base_url + "create_interpreter/"
retrieve_update_destroy_interpreter_endpoint = base_url + "create_interpreter/retrive_update_destroy_interpreter/<int:pk>/"


last_10_definitions_endpoint = base_url + "last_10_definitions/"
category_options_endpoint = base_url + "category_options/"
individual_description_endpoint = base_url + "individual_description/"

# Definition endpoints
definition_result_list_endpoint = base_url + "definition_result_list/"


# Call endpoints
create_call_endpoint = base_url + "create_call/"
retrieve_active_call_endpoint = base_url + "retrive_active_call/"
set_call_to_inactive_endpoint = base_url + "set_call_to_inactive/"
last_inactive_call = base_url + "last_inactive_call/"

# WorkDay endpoints
retrieve_work_day_endpoint = base_url + "retrive_work_day/"
retrieve_active_work_day_endpoint = base_url + "retrieve_active_work_day/"


# WorkMonth endpoints
retrieve_delete_work_month_endpoint = base_url + "retrive_delete_work_month/"
retrieve_is_current_work_month_endpoint = base_url + "retrieve_is_current_work_month/"
retrieve_current_work_month_endpoint = base_url + "retrieve_current_work_month/"


# Verifier endpoints
day_month_current_verifier_endpoint = base_url + "day_month_current_verifier/"

