from django.db.models import Model, CharField, ForeignKey, CASCADE, SET_NULL, ManyToManyField
from interpreter.models import Interpreter

# Create your models here.

"""
class English(Model):
    name = CharField(verbose_name="English", max_length=50, blank=False, null=False, unique=True)
    creator = ForeignKey(to=Interpreter, null=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name


class Spanish(Model):
    name = CharField(verbose_name="Spanish", max_length=50, blank=False, null=False, unique=True)
    creator = ForeignKey(to=Interpreter, null=True, on_delete=SET_NULL)

    def __str__(self):
        return self.name


class Category(Model):
    name = CharField(verbose_name="Category", max_length=100, blank=False, null=False, unique=True)

    def __str__(self):
        return self.name


class Abbreviation(Model):
    text = CharField(verbose_name="Abbreviation", max_length=30, blank=False, null=False, unique=True)

    def __str__(self):
        return self.text


class Definition(Model):
    text = CharField(verbose_name="Definition", max_length=500, blank=False, null=False)

    english = ManyToManyField(to=English)
    spanish = ManyToManyField(to=Spanish)
    category = ForeignKey(to=Category, null=True, on_delete=SET_NULL)
    abbreviation = ManyToManyField(to=Abbreviation, blank=True)

    def __str__(self):
        return str(self.text)[:12].capitalize() + "..."
    
"""
