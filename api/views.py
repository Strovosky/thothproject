from django.shortcuts import render
from rest_framework.decorators import api_view
from main.models import Definition, Category, English, Spanish, Abbreviation
from main.serializers import DefinitionSerializer, IndividualDefinitionSerializer, CategorySerializer, EnglishSerializer, SpanishSerializer, AbbreviationSerializer
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
    serialized_definitions = DefinitionSerializer(definitions, many=True).data
    return Response(serialized_definitions, status=200)

@api_view(["GET"])
def individual_word(request):
    "This view will provide the information of a specifict definition"
    id = int(request.GET["id_definition"])
    try:
        definition = Definition.objects.get(id=id)
        serialized_definition = IndividualDefinitionSerializer(definition).data
        return Response(serialized_definition, status=200)
    except:
        return Response({"definition_error":"No definition was found with that id."}, status=400)


@api_view(["POST"])
def create_english_word(request):
    """This api view will create a english instance"""
    serialized_english_word = EnglishSerializer(data=request.data)
    if serialized_english_word.is_valid(raise_exception=True):
        serialized_english_word.save()
        return Response(serialized_english_word.data, status=200)


""" THIS ONE IS ONLY A TEST
@api_view(["POST"])
def create_word(request):
    "This view will create a new word"
    if request.data:
        # We're gonna try this example as if ENGLISH AND SPANISH DON'T EXIST!!!
        category = Category.objects.get(name=request.data["category"])
        serialized_category = CategorySerializer(category)
        serialized_english = EnglishSerializer({"name":request.data["english"]})
        serialized_spanish = SpanishSerializer({"name":request.data["spanish"]})
        if serialized_english.is_valid(raise_exception=True) and serialized_spanish.is_valid(raise_exception=True):
            serialized_spanish.save()
            serialized_english.save()
        else:
            return Response({"error":"Problem with Spanish and English serializers valid info and creation."})
        if request.data["abbreviation"]:
            serialized_abbreviation = AbbreviationSerializer({"text":request.data["abbreviation"]})
            if serialized_abbreviation.is_valid(raise_exception=True):
                serialized_abbreviation.save()
        serialized_definition = IndividualDefinitionSerializer({
            "english":serialized_english.data,
            "spanish":serialized_spanish.data,
            "category":serialized_category.data,
            "abbreviation":serialized_abbreviation.data,
            "text":request.data["text"]
        })
        if serialized_definition.is_valid():
            serialized_definition.save()
            return Response(serialized_definition.data, status=200)
        else:
            return Response({"error":"Error when creating the definition"}, status=500)

        
    #serialized_definition = IndividualDefinitionSerializer(data=request.data)
    # I HAVE TO CREATE A SERIALIZER FOR ENGLISH, SPANISH, ABBREVIATION...
    #if serialized_definition.is_valid(raise_exception=True):
    #    print(serialized_definition.data)
    #    instance = serialized_definition.save()
    #    return Response(serialized_definition.data, status=200)
    return Response(request.data, status=200)"""










