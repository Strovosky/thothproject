from django.shortcuts import render
from rest_framework.decorators import api_view
from main.models import Definition
from main.serializers import Last10DefinitionsSerializer
from rest_framework.response import Response

# Create your views here.



@api_view(["GET"])
def category_options(request):
    "This view will provide the categories created manually"
    categories = {
        "medicine":"medicine",
        "social_programs":"social programs",
        "car_insurance":"car insurance",
        "legal":"legal",
        "finance":"finance"
        }
    return Response(categories)

@api_view(["GET"])
def last_10_definitions(request):
    "This view will provide the last 10 definitions"
    definitions = Definition.objects.order_by("-id")[0:10]
    serialized_definitions = Last10DefinitionsSerializer(definitions, many=True).data
    return Response(serialized_definitions)










