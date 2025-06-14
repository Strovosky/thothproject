from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from django.utils.timezone import make_aware, now, localtime
from django.db.models import Q

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
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView, RetrieveAPIView, ListAPIView
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
    """
    This view will authenticate the user and return the token. I will also create a WorkMonth and WorkDay if required.
    """
    
    def create_work_month(self, inter):
        """This function will create a new WorkMonth if it doesn't exist."""
        current_month = WorkMonth.objects.filter(is_current=True, interpreter=inter)
        if not current_month.exists():
            # Create a new WorkMonth if it doesn't exist
            if localtime(timezone.now()).day >= 15:
                # If today is after the 15th, create a new WorkMonth with end date on the 14th of the next month
                current_month = WorkMonth.objects.create(
                    start_date=timezone.now(),
                    end_date=localtime(timezone.now()).replace(day=14).replace(month=localtime(timezone.now()).month + 1),
                    is_current=True,
                    interpreter=inter
                    )
                print(f"New month created: {current_month}")
                return current_month
            elif localtime(timezone.now()).day < 15:
                # If today is before or on the 15th, create a new WorkMonth with end date on the 14th of the current month
                current_month = WorkMonth.objects.create(
                    start_date=timezone.now(),
                    end_date=localtime(timezone.now()).replace(day=14),
                    is_current=True,
                    interpreter=inter
                    )
                print(f"New month created: {current_month}")
                return current_month
        else:
            # If a WorkMonth already exists and is active. We'll check if it's end_date is older than today, if so...
            # we'll set it is_current to False and create a new WorkMonth.
            if current_month.count() > 1:
                for c_month in current_month:
                    if not localtime(c_month.end_date) or localtime(c_month.end_date) < localtime(timezone.now()):
                        c_month.is_current = False
                        c_month.save()
            elif not current_month.exists():
                self.create_work_month()
            else:
                print(f"The current month is the same one: {current_month.first()}")
                return current_month.first()
            
    
    def create_work_day(self, inter):
        """
        This function will create a new WorkDay if it doesn't exist for the current WorkMonth.
        """
        current_work_month = self.create_work_month(inter)
        current_work_day = WorkDay.objects.filter(active=True, interpreter=inter)
        if current_work_day.count() == 0:
            # Create a new WorkDay if it doesn't exist
            work_day =WorkDay.objects.create(
                active=True,
                work_month=current_work_month,
                interpreter=inter,
            )
            print(f"Work day created: {work_day} for month {current_work_month.start_date} - {current_work_month.end_date}")
        # If a WorkDay already exists and is active, we'll check if it's day_end is older than today, if so...
        # we'll set it is_active to False and create a new WorkDay.
        elif current_work_day.count() > 1:
            for c_day in current_work_day:
                c_day.active = False
                c_day.save()
            self.create_work_day(inter)
        else:
            # IF a WorkDay already exists, we'll verify if the date is the same as today's.
            print(f"This is WorkDay date {current_work_day.first().day_start.date()} and this is today's {timezone.now().date()}")
            if localtime(current_work_day.first().day_start).date() == localtime(timezone.now()).date():
                # If it's the same, we get that day.
                print(f"Current work_day obteined: {current_work_day.first()}")
                return current_work_day.first()
            else:
                # If not the same, we set active = False and create the new day.
                c_day = current_work_day.first()
                c_day.active = False
                c_day.save()
                print(f"{c_day} is suppossed to be changed.")
                self.create_work_day(inter)
                    

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

class RetriveActiveCallAPIView(ListAPIView):
    """
    This API view will retrive the active call for the current user.
    """
    queryset = Call.objects.filter(active=True)
    serializer_class = CallSerializer

    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

class UpdateActiveCallAPIView(UpdateAPIView):
    """
    This view will update the call.
    """
    queryset = Call.objects.all()
    serializer_class = CallSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be overridden to provide a queryset.
        """
        if not self.request.user.is_authenticated:
            return Call.objects.none()
        if self.queryset is not None:
            return self.queryset.filter(interpreter=self.request.user)
        raise NotImplementedError(
            f"{self.__class__.__name__} must define a queryset or override get_queryset()."
        )

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
        day_work = self.queryset.filter(active=True, interpreter=self.request.user)
        if day_work.count() == 1:
            if str(localtime(day_work.first().day_start).date()) == str(today):
                # If the active day_work is today, we serialize it and return it.
                serialized_day_work = self.get_serializer(day_work.first()).data
                return Response(serialized_day_work, status=status.HTTP_200_OK)
            else:
                return(Response({"error":f"day_start {localtime(day_work.first().day_start).date()} and {today} are different"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR))
        elif day_work.count() > 1:
            return Response({"error":f"More than one day with the date {today}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Else, we serialize an empty WorkDay.
            return Response({"error":f"No work_day found with date {today}"}, status=status.HTTP_404_NOT_FOUND)


    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

class RetrieveActiveWorkDayAPIView(ListAPIView):
    """
    This API view will retrieve the active WorkDay for the current user.
    """
    queryset = WorkDay.objects.filter(active=True)
    serializer_class = WorkDaySerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method will filter the queryset to only include the WorkDay that is active and belongs to the user.
        """
        if not self.request.user.is_authenticated:
            return WorkDay.objects.none()
        return self.queryset.filter(interpreter=self.request.user)

class RetriveDestroyWorkMonthAPIView(RetrieveUpdateDestroyAPIView):
    """
    This API view will retrieve or destroy a WorkMonth.
    """
    queryset = WorkMonth.objects.all()
    serializer_class = WorkMonthSerializer
    lookup_field = "is_current"
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class RetrieveIsCurrentWorkMonthAPIView(ListAPIView):
    """
    This API view will yield the current WorkMonth for the current user.
    """
    queryset = WorkMonth.objects.filter(is_current=True)
    serializer_class = WorkMonthSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

class LastInactiveCallAPIView(ListAPIView):
    """
    This APIView will return the last inactive call for the current user.
    """

    queryset = Call.objects.filter(active=False)
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CallSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(interpreter=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
class DefinitionListAPIView(ListAPIView):
    """
    This API view will list all the definitions.
    """
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This function will filter the queryset to only include the definitions that match the search query.
        """
        word = self.kwargs.get("word", None)
        if word:
            return self.queryset.filter(Q(english__name__icontains=word) | Q(spanish__name__icontains=word) | Q(text__icontains=word) | Q(abbreviation__text__icontains=word)).distinct()
        
class RetrieveCurrentWorkMonthAPIView(RetrieveAPIView):
    """
    This API view will retrieve a WorkMonth by its id.
    """
    queryset = WorkMonth.objects.all()
    serializer_class = WorkMonthSerializer
    lookup_field = "pk"
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This method will filter the queryset to only include the WorkMonth that is current and belongs to the user.
        """
        if not self.request.user.is_authenticated:
            return WorkMonth.objects.none()
        return self.queryset.filter(is_current=True, interpreter=self.request.user)
    
class DayMonthCurrentVerifierAPIView(APIView):
    """
    This API view will verify if the current WorkMonth and WorkDay is the same as the one in the request.
    """
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        current_work_month = WorkMonth.objects.filter(is_current=True, interpreter=request.user).first()
        if not current_work_month:
            return Response({"error": "No current work month found."}, status=status.HTTP_404_NOT_FOUND)
        current_work_day = WorkDay.objects.filter(active=True, interpreter=request.user).first()
        if not current_work_day:
            return Response({"error": "No current work day found."}, status=status.HTTP_404_NOT_FOUND)
        
        change = {"change_work_month": False, "change_work_day": False}

        # Let's work with the month first.
        if current_work_month.end_date.date() < localtime(timezone.now()).date():
            # If the current WorkMonth is older than today, we set its is_current to False and create a new WorkMonth.
            current_work_month.is_current = False
            current_work_month.save()
            # Create a new WorkMonth
            if localtime(timezone.now()).day >= 15:
                # If today is after the 15th, create a new WorkMonth with end date on the 14th of the next month
                current_work_month = WorkMonth.objects.create(
                    start_date=localtime(timezone.now()),
                    end_date=localtime(timezone.now()).replace(day=14).replace(month=localtime(timezone.now()).month + 1).replace(hour=23, minute=59, second=59),
                    is_current=True,
                    interpreter=request.user
                )
                change["change_work_month"] = True
                change["work_month"] = WorkMonthSerializer(current_work_month).data
            else:
                # If today is before or on the 15th, create a new WorkMonth with end date on the 14th of the current month
                current_work_month = WorkMonth.objects.create(
                    start_date=localtime(timezone.now()),
                    end_date=localtime(timezone.now()).replace(day=14, hour=23, minute=59, second=59),
                    is_current=True,
                    interpreter=request.user
                )
                change["change_work_month"] = True
                change["work_month"] = WorkMonthSerializer(current_work_month).data

        # Now let's work with the WorkDay.
        if current_work_day.day_start.date() != localtime(timezone.now()).date():
            # If the current WorkDay is not today, we set its active to False and create a new WorkDay.
            current_work_day.active = False
            current_work_day.save()
            work_day = WorkDay.objects.create(
                active=True,
                work_month=current_work_month,
                interpreter=request.user,
                day_start=localtime(timezone.now())
            )
            change["change_work_day"] = True
            change["work_day"] = WorkDaySerializer(work_day).data

        return Response(change, status=status.HTTP_200_OK)

