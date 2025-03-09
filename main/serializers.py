from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Definition



class Last10DefinitionsSerializer(ModelSerializer):
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
        return obj.english.first().name[0:20]
    def get_spanish(self, obj):
        return obj.spanish.first().name[0:20]
    def get_category(self, obj):
        return obj.category.name
    def get_text(self, obj):
        if len(obj.text) > 22:
            return obj.text[0:22] + "..."
        else:
            return obj.text
    def get_abbreviation(self, obj):
        try:
            obj.abbreviation.first().text
            return obj.abbreviation.first().text
        except:
            return ""












