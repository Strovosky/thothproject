# Here we'll store all of the endpoints


base_url = "http://localhost:8000/api/"

authenticate_interpreter = "http://127.0.0.1:8000/api/auth_interpreter/"
destroy_token_endpoint = "http://localhost:8000/api/destroy_token/"
create_interpreter_endpoint = "http://localhost:8000/api/create_interpreter/"
retrieve_update_destroy_interpreter_endpoint = "http://localhost:8000/api/create_interpreter/retrive_update_destroy_interpreter/<int:pk>/"


# Call endpoints
create_call_endpoint = "http://localhost:8000/api/create_call/"
retrieve_active_call_endpoint = base_url + "retrive_active_call/"
set_call_to_inactive = base_url + "set_call_to_inactive/"
last_inactive_call = base_url + "last_inactive_call/"

# WorkDay endpoints
retrieve_work_day_endpoint = "http://localhost:8000/api/retrive_work_day/"


# WorkMonth endpoints
retrieve_delete_work_month_endpoint = "http://localhost:8000/api/retrive_delete_work_month/"
