from django.db.models import Model, CharField, IntegerField, ForeignKey, CASCADE, BooleanField, DateTimeField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from interpreter.models import Interpreter

# Create your models here.



class WorkMonth(Model):
    """
    This model represents a month of work and how much was earned.
    """
    start_date = DateTimeField(verbose_name=_("Start Date"), help_text=_("The 15th of each month."), unique=True)
    end_date = DateTimeField(verbose_name=_("End Date"), help_text=_("The 14th of each month."), unique=True)

    dolar_peso_rate = IntegerField(verbose_name=_("Dolar to Peso rate"), help_text=_("The rate of the dollar to peso for this month."), default=4500)
    pay_rate_min = IntegerField(verbose_name=_("Pay rate"), help_text=_("The pay per minute for this month."), default=0.18)
    
    is_current = BooleanField(verbose_name=_("Is current month?"), help_text=_("Is this the current month?"), default=False)

    interpreter = ForeignKey(Interpreter, verbose_name=_("Interpreter"), help_text=_("The interpreter who worked this month."), on_delete=CASCADE, related_name="work_months")

    def __str__(self):
        return self.start_date.strftime("%B %Y")
    

class WorkDay(Model):
    """
    This model represents a day of work.
    """
    day_start = DateTimeField(verbose_name=_("Call started at"), help_text=_("The time the current work day started."), auto_now_add=True)
    day_end = DateTimeField(verbose_name=_("Call ended at"), help_text=_("The time the work day ended."), default=timezone.now().replace(hour=23, minute=59, second=59))

    active = BooleanField(verbose_name=_("Is_active?"), help_text=_("Is this day active?"), default=False)

    work_month = ForeignKey(WorkMonth, verbose_name=_("Work month"), help_text=_("The month this work day belongs to."), on_delete=CASCADE, related_name="work_days")
    interpreter = ForeignKey(Interpreter, verbose_name=_("Interpreter"), help_text=_("The interpreter who worked this day."), on_delete=CASCADE, related_name="work_days")


    def __str__(self):
        return f"{self.interpreter.username}'s day worked on {self.day_start.strftime('%d/%m/%Y')}"
    



class Call(Model):
    """
    This model represents a call made during a work day.
    """
    call_start = DateTimeField(verbose_name=_("Call started at"), help_text=_("The time the current call started."), auto_now_add=True)
    call_end = DateTimeField(verbose_name=_("Call ended at"), help_text=_("The time the current call ended."), default=None, null=True, blank=True)

    active = BooleanField(verbose_name=_("Is active?"), help_text=_("Is this call active?"), default=False)

    note = CharField(verbose_name=_("Note"), help_text=_("A note for this call."), max_length=255, default="", blank=True)

    work_day = ForeignKey(WorkDay, verbose_name=_("Work day"), help_text=_("The work day this call belongs to."), on_delete=CASCADE, related_name="calls")
    interpreter = ForeignKey(Interpreter, verbose_name=_("Interpreter"), help_text=_("The interpreter who made this call."), on_delete=CASCADE, related_name="calls")


    def __str__(self):
        return f"Call for {self.interpreter.username} at {self.call_start.strftime('%d/%m/%Y %H:%M')}"

