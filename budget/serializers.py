from rest_framework.serializers import ModelSerializer
from .models import Call
from django.utils.translation import gettext_lazy as _



class CallSerializer(ModelSerializer):
    class Meta:
        model = Call
        fields = [
            "id",
            "interpreter",
            "client",
            "start_time",
            "end_time",
            "status",
            "notes"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "interpreter": {"required": True, "error_messages": {"required": _("Interpreter is required.")}},
            "client": {"required": True, "error_messages": {"required": _("Client is required.")}},
            "status": {"required": True, "error_messages": {"required": _("Status is required.")}},
        }






