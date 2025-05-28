from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Call, WorkDay, WorkMonth
from django.utils.translation import gettext_lazy as _


class CallSerializer(ModelSerializer):
    """
    Standard serializer for the Call model.
    """

    interpreter = SerializerMethodField(read_only=True)
    work_day = SerializerMethodField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id",
            "call_start",
            "call_end",
            "active",
            "note",
            "work_day",
            "interpreter"
        ]
        read_only_fields = ["id", "call_start"]
        extra_kwargs = {
            "interpreter": {"required": True, "error_messages": {"required": _("Interpreter is required.")}},
            "work_day": {"required": True, "error_messages": {"required": _("Work_day is required.")}}
        }

    def get_interpreter(self, obj):
        """
        Returns the username of the interpreter associated with the call.
        """
        return obj.interpreter.username if obj.interpreter else None
    
    def get_work_day(self, obj):
        """
        Returns the ID of the work day associated with the call.
        """
        return obj.work_day.call_start if obj.work_day else None

class WorkDaySerializer(ModelSerializer):
    """
    Standard serializer for the WorkDay model.
    """

    interpreter = SerializerMethodField(read_only=True)
    work_month = SerializerMethodField(read_only=True)

    class Meta:
        model = WorkDay
        fields = [
            "id",
            "day_start",
            "day_end",
            "active",
            "work_month",
            "interpreter"
        ]
        read_only_fields = ["id", "day_start"]
        extra_kwargs = {
            "interpreter": {"required": True, "error_messages": {"required": _("Interpreter is required.")}},
            "work_month": {"required": True, "error_messages": {"required": _("Work_month is required.")}}
        }

    def get_interpreter(self, obj):
        """
        Returns the username of the interpreter associated with the work day.
        """
        return obj.interpreter.username if obj.interpreter else None
    
    def get_work_month(self, obj):
        """
        Returns the ID of the work month associated with the work day.
        """
        return obj.work_month.start_date if obj.work_month else None

class WorkMonthSerializer(ModelSerializer):
    """
    Standard serializer for the WorkMonth model.
    """

    interpreter = SerializerMethodField(read_only=True)

    class Meta:
        model = WorkMonth
        fields = [
            "id",
            "start_date",
            "end_date",
            "dolar_peso_rate",
            "pay_rate_min",
            "is_current",
            "interpreter"
        ]
        read_only_fields = ["id", "start_date", "end_date"]
        extra_kwargs = {
            "interpreter": {"required": True, "error_messages": {"required": _("Interpreter is required.")}}
        }

    def get_interpreter(self, obj):
        """
        Returns the username of the interpreter associated with the work month.
        """
        return obj.interpreter.username if obj.interpreter else None


