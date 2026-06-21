from django.urls import path

from .views import DashboardStatsView

from .views import InterviewReportView


urlpatterns = [
    path(
        'dashboard/',  # The URL path that users will visit
        DashboardStatsView.as_view(),  # Convert the class-based view to a callable view
        name='dashboard-stats'  # A unique name for this URL pattern (useful for URL reversal)
    ),
    path(
        'interview/<int:interview_id>/',
        InterviewReportView.as_view(),
        name='interview-report'
    ),
]
