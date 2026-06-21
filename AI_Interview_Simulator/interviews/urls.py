from django.urls import path

from .views import (
    InterviewCreateView,
    InterviewListView,
    InterviewQuestionsView,
    SubmitAnswerView,
    AnswerListView
)

urlpatterns = [
    path('create/', InterviewCreateView.as_view(), name='create-interview'),
    
    path('', InterviewListView.as_view(), name='list-interviews'),
    
    path(
        '<int:interview_id>/questions/',
        InterviewQuestionsView.as_view(),
        name='interview-questions'
    ),
    
    path(
        'submit-answer/',
        SubmitAnswerView.as_view(),
        name='submit-answer'
    ),
    
    path(
        'answers/',
        AnswerListView.as_view(),
        name='answer-list'
    ),
]