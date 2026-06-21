from rest_framework import serializers
from django.db.models import Avg
from .models import Interview, Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class InterviewSerializer(serializers.ModelSerializer):
    average_score = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()

    # Indented to be INSIDE the InterviewSerializer
    class Meta:
        model = Interview
        fields = [
            'id',
            'role',
            'difficulty',
            'created_at',
            'average_score',
            'completed'
        ]

    # Indented to be INSIDE the InterviewSerializer
    def get_average_score(self, obj):
        result = Answer.objects.filter(
            interview=obj
        ).aggregate(avg=Avg('score'))

        return round(result['avg'], 1) if result['avg'] else 0

    # Indented to be INSIDE the InterviewSerializer
    def get_completed(self, obj):
        return Answer.objects.filter(
            interview=obj
        ).count() >= 5