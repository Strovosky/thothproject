# Here we'll create the serializer for the interpreter model

from .models import Interpreter
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class InterpreterSerializer(ModelSerializer):
    """This is the serializer for the Interpreter model"""

    class Meta:
        model = Interpreter
        fields = [
            "id",
            "email",
            "password",
            "username",
            "is_admin",
            "phone",
            "is_active"
        ]

