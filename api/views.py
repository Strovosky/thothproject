from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from main.models import Definition, Category, English, Spanish, Abbreviation
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate

from interpreter.models import Interpreter
from interpreter.serializers import InterpreterSerializer
from main.serializers import DefinitionSerializer, IndividualDefinitionSerializer, CategorySerializer, EnglishSerializer, SpanishSerializer, AbbreviationSerializer
from rest_framework.response import Response

# To create generic API VIEWS
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.mixins import CreateModelMixin

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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def last_10_definitions(request):
    "This view will provide the last 10 definitions"
    definitions = Definition.objects.order_by("-id")[0:10]
    serialized_definitions = DefinitionSerializer(definitions, many=True).data
    return Response(serialized_definitions, status=200)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_english_word(request):
    """This api view will create a english instance"""
    serialized_english_word = EnglishSerializer(data=request.data)
    if serialized_english_word.is_valid(raise_exception=True):
        serialized_english_word.save()
        return Response(serialized_english_word.data, status=200)


class AuthenticateInterpreterAPIView(APIView):
    """This view will will authenticate the user and return the token."""

    def post(self, request, *args, **kwargs):
        if not request.data.get("email") or not request.data.get("password"):
            return Response({"error":"No email or password provided."}, status=status.HTTP_400_BAD_REQUEST)
        interpreter = authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        if interpreter is None:
            return Response({"error":"Wrong credentials provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=interpreter)
        response = Response({"token":token.key, "interpreter_id":interpreter.id}, status=status.HTTP_200_OK)
        response.set_cookie('auth_token', token.key, httponly=True)
        return response


class DestroyCurrentToken(APIView):
    """This API View will destroy the token when the user does a logout. """

    def post(self, request, *args, **kwargs):
        token_key = request.data["token"]
        try:
            token = Token.objects.get(key=token_key)
            token.delete()
            print("this part ok")
            return Response({"token_destroyed":True}, status=status.HTTP_200_OK)
        except:
            return Response({"token_destroyed":False}, status=status.HTTP_404_NOT_FOUND)
        



class CreateInterpreterAPIView(CreateAPIView):
    """This API view will create a new user."""
    queryset = Interpreter.objects.all()
    serializer_class = InterpreterSerializer

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            instance.set_password(serializer.validated_data["password"])
            instance.save()

class RetrieveUpdateDestroyInterpreterAPIView(RetrieveUpdateDestroyAPIView):
    """This view will let you retrieve, update, and destroy an interpreter"""
    queryset = Interpreter.objects.all()
    serializer_class = InterpreterSerializer
    lookup_field = "pk"

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """We'll create a partial update"""
        """NOT WORKING"""
        interpreter = self.get_object()
        interpreters = self.get_queryset()
        if serializer.validated_data["username"]:
            if interpreters.filter(username=serializer.validated_data["username"]).count() > 0:
                return {"error":"Username already exists"}
            else:
                interpreter.username = serializer.validated_data["username"]
        if serializer.validated_data["email"]:
            if interpreters.filter(email=serializer.validated_data["email"]).count() > 0:
                return {"error":"Email already exists"}
            else:
                interpreter.email = serializer.validated_data["email"]
        if serializer.validated_data["phone"]:
            if interpreters.filter(phone=serializer.validated_data["phone"]).count() > 0:
                return {"error":"Phone already exists"}
            else:
                interpreter.phone = serializer.validated_data["phone"]
        if serializer.validated_data["password"]:
            if len(serializer.validated_data["password"]) < 5:
                return {"error":"Password is too short"}
            elif len(serializer.validated_data["password"]) > 20:
                return {"error":"Password is too long"}
            interpreter.set_password(serializer.validated_data["password"])
        interpreter.save()

    def perform_destroy(self, instance):
        """We won't destroy the instance, we'll simply set it to instance.is_active = False"""
        instance.is_active = False
        instance.save()


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










