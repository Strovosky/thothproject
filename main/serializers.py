from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Definition, English, Spanish, Abbreviation



class DefinitionSerializer(ModelSerializer):
    "Here we have the basic Category Serializer"

    english = SerializerMethodField(read_only=True)
    spanish = SerializerMethodField(read_only=True)
    category = SerializerMethodField(read_only=True)
    abbreviation = SerializerMethodField(read_only=True)
    text = SerializerMethodField(read_only=True)

    class Meta:
        model = Definition
        fields = [
            'id',
            'text',
            'english',
            'spanish',
            'category',
            'abbreviation'
        ]

    def get_english(self, obj):
        return obj.english.first().name
    def get_spanish(self, obj):
        return obj.spanish.first().name
    def get_category(self, obj):
        return obj.category.name
    def get_text(self, obj):
        return obj.text
    def get_abbreviation(self, obj):
        try:
            obj.abbreviation.first().text
            return obj.abbreviation.first().text
        except:
            return ""



class IndividualDefinitionSerializer(ModelSerializer):
    "Here we have the basic Category Serializer"

    english = SerializerMethodField(read_only=True)
    spanish = SerializerMethodField(read_only=True)
    category = SerializerMethodField(read_only=True)
    abbreviation = SerializerMethodField(read_only=True)
    text = SerializerMethodField(read_only=True)

    class Meta:
        model = Definition
        fields = [
            'id',
            'text',
            'english',
            'spanish',
            'category',
            'abbreviation'
        ]

    def get_english(self, obj):
        return {"names":[english.name for english in obj.english.all()]}
    def get_spanish(self, obj):
        return {"names":[spanish.name for spanish in obj.spanish.all()]}
    def get_category(self, obj):
        return obj.category.name
    def get_text(self, obj):
        return obj.text
    def get_abbreviation(self, obj):
        return {"texts":[abb.text for abb in obj.abbreviation.all()]}


class EnglishSerializer(ModelSerializer):
    "This will serialize the English Model"
    class Meta:
        model = English
        fields = [
            "name"
        ]


class SpanishSerializer(ModelSerializer):
    "This will serialize the Spanish Model"
    class Meta:
        model = Spanish
        fields = [
            "name"
        ]


class CategorySerializer(ModelSerializer):
    "This will serialize the Category Model"
    class Meta:
        model = Category
        fields = [
            "name"
        ]


class AbbreviationSerializer(ModelSerializer):
    "This will serialize the Abbreviation Model"
    text = SerializerMethodField(read_only=True)
    class Meta:
        model = Abbreviation
        fields = [
            "text"
        ]

    def get_text(self, obj):
        return {"texts":[abb.text for abb in obj.abbreviation.all()]}
    


