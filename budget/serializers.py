from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Call, WorkDay, WorkMonth
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now, localdate, localtime


class CallSerializer(ModelSerializer):
    """
    Standard serializer for the Call model.
    """

    #interpreter = SerializerMethodField(read_only=True)
    #work_day = SerializerMethodField(read_only=True)
    call_start_local_time = SerializerMethodField(read_only=True)
    call_end_local_time = SerializerMethodField(read_only=True)

    class Meta:
        model = Call
        fields = [
            "id",
            "call_start",
            "call_start_local_time",
            "call_end",
            "call_end_local_time",
            "time_call",
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

    def get_call_start_local_time(self, obj):
        """
        Return the call_start but formatted for the local city.
        """
        local_time = localtime(obj.call_start)
        return f"{local_time.strftime('%B/%d/%y')} at {local_time.strftime('%l:%M:%p')}"
    
    def get_call_end_local_time(self, obj):
        """
        Return the call_end but formatted for the local city.
        """
        local_time = localtime(obj.call_end)
        return f"{local_time.strftime('%B/%d/%y')} at {local_time.strftime('%l:%M %p')}"

    #def get_interpreter(self, obj):
    #    """
    #    Returns the username of the interpreter associated with the call.
    #    """
    #    return obj.interpreter.username if obj.interpreter else None
    
    #def get_work_day(self, obj):
    #    """
    #    Returns the ID of the work day associated with the call.
    #    """
        #return obj.work_day.call_start if obj.work_day else None

class WorkDaySerializer(ModelSerializer):
    """
    Standard serializer for the WorkDay model.
    """

    interpreter = SerializerMethodField(read_only=True)
    work_month = SerializerMethodField(read_only=True)
    day_start_local = SerializerMethodField(read_only=True)
    day_end_local = SerializerMethodField(read_only=True)
    num_calls = SerializerMethodField(read_only=True)
    time_worked = SerializerMethodField(read_only=True)

    class Meta:
        model = WorkDay
        fields = [
            "id",
            "day_start",
            "day_start_local",
            "day_end",
            "day_end_local",
            "time_worked",
            "active",
            "work_month",
            "work_month_id",
            "interpreter",
            "num_calls"
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
    
    def get_work_month_id(self, obj):
        """
        Returns the ID of the work month associated with the work day.
        """
        return obj.work_month.id if obj.work_month else None
    
    def get_day_start_local(self, obj):
        """
        Returns the datetime the work_day started in local time.
        """
        local_datetime = localtime(obj.day_start)
        return local_datetime

    def get_day_end_local(self, obj):
        """
        Returns the datetiem the work_day ended in local time
        """
        local_datetime = localtime(obj.day_end)
        return local_datetime
    
    def get_num_calls(self, obj):
        """
        Returns the number of calls a workday has.
        """
        return obj.calls.count()
    
    def get_time_worked(self, obj):
        """
        Returns the hours and minutes worked today.
        """
        try:
            # In case obj.time_worked.seconds is none because no calls have been placed.
            print(type(obj.time_worked))
            print(obj.time_worked.seconds)
            all_seconds = obj.time_worked.seconds
            hours = str(all_seconds // 3600)
            minutes = str((all_seconds % 3600) // 60)
            seconds = str(all_seconds % 60)

            return f"{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}"
        except:
            return "00:00:00"

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


