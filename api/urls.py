# Here we have all the API urls
from django.urls import path
from .views import last_10_definitions, category_options, individual_word, create_english_word, CreateInterpreterAPIView, RetrieveUpdateDestroyInterpreterAPIView, AuthenticateInterpreterAPIView, DestroyCurrentToken, CreateCallAPIView, RetriveyWorkDayAPIView, RetriveDestroyWorkMonthAPIView, RetriveActiveCallAPIView, UpdateActiveCallAPIView, LastInactiveCallAPIView, DefinitionListAPIView, RetrieveCurrentWorkMonthAPIView, RetrieveActiveWorkDayAPIView, RetrieveIsCurrentWorkMonthAPIView, DayMonthCurrentVerifierAPIView, ListAllInterpretersAPIView

urlpatterns = [
    path(route="last_10_definitions/", view=last_10_definitions, name="last_10_definitions"),
    path(route="category_options/", view=category_options, name="category_options"),
    path(route="individual_description/", view=individual_word, name="individual_description"),
    path(route="create_english_word/", view=create_english_word, name="create_english_word"),
    path(route="create_interpreter/", view=CreateInterpreterAPIView.as_view(), name="create_interpreter"),
    path(route="list_all_interpreters/", view=ListAllInterpretersAPIView.as_view(), name="list_all_interpreters"),
    path(route="retrive_update_destroy_interpreter/<int:pk>/", view=RetrieveUpdateDestroyInterpreterAPIView.as_view(), name="retrive_update_destroy_interpreter"),
    path(route="auth_interpreter/", view=AuthenticateInterpreterAPIView.as_view(), name="auth_interpreter"),
    path(route="destroy_token/", view=DestroyCurrentToken.as_view(), name="destroy_token"),
    path(route="create_call/", view=CreateCallAPIView.as_view(), name="create_call"),
    path(route="retrive_active_call/", view=RetriveActiveCallAPIView.as_view(), name="retrive_active_call"),
    path(route="set_call_to_inactive/<int:pk>/", view=UpdateActiveCallAPIView.as_view(), name="set_call_to_inactive"),
    path(route="retrive_work_day/<str:day_start>/", view=RetriveyWorkDayAPIView.as_view(), name="retrive_work_day"),
    path(route="retrieve_active_work_day/", view=RetrieveActiveWorkDayAPIView.as_view(), name="retrieve_active_work_day"),
    path(route="last_inactive_call/", view=LastInactiveCallAPIView.as_view(), name="last_inactive_call"),
    path(route="definition_result_list/<str:word>/", view=DefinitionListAPIView.as_view(), name="definition_result_list"),
    path(route="day_month_current_verifier/", view=DayMonthCurrentVerifierAPIView.as_view(), name="day_month_current_verifier"),
    path(route="retrieve_is_current_work_month/", view=RetrieveIsCurrentWorkMonthAPIView.as_view(), name="retrieve_is_current_work_month"),
    path(route="retrieve_current_work_month/<int:pk>/", view=RetrieveCurrentWorkMonthAPIView.as_view(), name="retrieve_current_work_month"),
]






