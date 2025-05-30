from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from django.utils.timezone import make_aware

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

from budget.models import WorkMonth, WorkDay, Call
from budget.serializers import CallSerializer, WorkMonthSerializer, WorkDaySerializer

# To create generic API VIEWS
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, ListModelMixin
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


    """
    This part of the code will verify if there's a current WorkMonth and WorkDay already created, else it will create a new one.
    """
    
    def create_work_month(self, inter):
        """This function will create a new WorkMonth if it doesn't exist."""
        if not WorkMonth.objects.filter(is_current=True, interpreter=inter).exists():
            # Create a new WorkMonth if it doesn't exist
            if timezone.now().day >= 15:
                # If today is after the 15th, create a new WorkMonth with end date on the 14th of the next month
                current_month = WorkMonth.objects.create(
                    start_date=timezone.now(),
                    end_date=timezone.now().replace(day=14).replace(month=timezone.now().month + 1),
                    is_current=True,
                    interpreter=inter
                    )
                return current_month
            elif timezone.now().day < 15:
                # If today is before or on the 15th, create a new WorkMonth with end date on the 14th of the current month
                current_month = WorkMonth.objects.create(
                    start_date=timezone.now(),
                    end_date=timezone.now().replace(day=14),
                    is_current=True,
                    interpreter=inter
                    )
                return current_month
        else:
            # If a WorkMonth already exists and is active. We'll check if it's end_date is older than today, if so...
            # we'll set it is_current to False and create a new WorkMonth.
            current_month = WorkMonth.objects.filter(is_current=True, interpreter=inter)
            if current_month.count() > 1:
                for c_month in WorkMonth.objects.filter(is_current=True, interpreter=inter):
                    if not c_month.end_date or c_month.end_date < timezone.now():
                        c_month.is_current = False
                        c_month.save()
            elif not WorkMonth.objects.filter(is_current=True, interpreter=inter).exists():
                self.create_work_month()
            else:
                return current_month.first()
            
    
    def create_work_day(self, inter):
        """
        This function will create a new WorkDay if it doesn't exist for the current WorkMonth.
        """
        current_work_month = self.create_work_month(inter)
        current_work_day = WorkDay.objects.filter(active=True, interpreter=inter)
        if not current_work_day.exists():
            # Create a new WorkDay if it doesn't exist
            WorkDay.objects.create(
                active=True,
                work_month=current_work_month,
                interpreter=inter,
            )
            print(f"Work day created: {timezone.now().date()} for month {current_work_month.start_date} - {current_work_month.end_date}")
        else:
            # If a WorkDay already exists and is active, we'll check if it's day_end is older than today, if so...
            # we'll set it is_active to False and create a new WorkDay.
            if current_work_day.count() > 1:
                for c_day in WorkDay.objects.filter(active=True, interpreter=inter):
                    if c_day.day_end < timezone.now():
                        c_day.active = False
                        c_day.save()
            if not current_work_day.exists():
                self.create_work_day()
            if current_work_day.count() == 1:
                return current_work_day.first()
                    

                    

    def post(self, request, *args, **kwargs):
        
        """
        This part of the code will do the authentication of the user.
        """
        if not request.data.get("email") or not request.data.get("password"):
            return Response({"error":"No email or password provided."}, status=status.HTTP_400_BAD_REQUEST)
        interpreter = authenticate(request, email=request.data.get("email"), password=request.data.get("password"))

        self.create_work_month(interpreter)
        self.create_work_day(interpreter)

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

class CreateCallAPIView(CreateAPIView):
    """
    This API view will cretate a new call.
    """
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class RetriveyWorkDayAPIView(RetrieveModelMixin, GenericAPIView):
    """
    This API view will retrieve a WorkDay by active = True and if current day is today.
    """
    queryset = WorkDay.objects.all()
    serializer_class = WorkDaySerializer
    lookup_field = "day_start"
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method will filter the queryset to only include the WorkDay that is active and whose day_start is today.
        """

    def retrieve(self, request, *args, **kwargs):
        today = self.kwargs.get("day_start")
        #utc_today = make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        day_work = self.queryset.filter(active=True, interpreter=self.request.user).first()
        if str(day_work.day_start.date()) == today:
            # If the active day_work is today, we serialize it and return it.
            serialized_day_work = self.get_serializer(day_work).data
            return Response(serialized_day_work, status=status.HTTP_200_OK)
        else:
            # Else, we serialize an empty WorkDay.
            day_work = self.queryset.filter(day_start=None, interpreter=self.request.user).first()
            serialized_day_work = self.get_serializer(day_work).data
            return Response(serialized_day_work, status=status.HTTP_404_NOT_FOUND)


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    

class RetriveDestroyWorkMonthAPIView(RetrieveUpdateDestroyAPIView):
    """
    This API view will retrieve or destroy a WorkMonth.
    """
    queryset = WorkMonth.objects.all()
    serializer_class = WorkMonthSerializer
    lookup_field = "is_current"
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]


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










