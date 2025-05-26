from rest_framework.serializers import ModelSerializer
from .models import Call
from django.utils.translation import gettext_lazy as _



class CallSerializer(ModelSerializer):
    class Meta:
        model = Call
        fields = [
            "id",
            "interpreter",
            "call_start",
            "call_end",
            "active",
            "note",
            "work_day"
        ]
        read_only_fields = ["id", "call_start", "updated_at"]
        extra_kwargs = {
            "interpreter": {"required": True, "error_messages": {"required": _("Interpreter is required.")}},
            "client": {"required": True, "error_messages": {"required": _("Client is required.")}},
            "status": {"required": True, "error_messages": {"required": _("Status is required.")}},
        }






