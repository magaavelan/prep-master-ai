from django.urls import path

from frontend_views import (
    LoginPageView,
    HistoryDashboardPageView,
    InterviewReportPageView,
    InterviewSessionPageView,
    InterviewSetupPageView,
    HomePageView,  # Updated import
)

urlpatterns = [
    # 1. Landing page is now the Login page
    path("", LoginPageView.as_view(), name="login"),
    
    # 2. Home page (home.html) to go to AFTER login
    path("home/", HomePageView.as_view(), name="home"),
    
    path("dashboard/", HistoryDashboardPageView.as_view(), name="dashboard"),
    path("history/", HistoryDashboardPageView.as_view(), name="history"),

    path(
        "interview/setup/",
        InterviewSetupPageView.as_view(),
        name="interview-setup",
    ),
    path(
        "interview/session/",
        InterviewSessionPageView.as_view(),
        name="interview-session",
    ),
    path(
        "interview/report/",
        InterviewReportPageView.as_view(),
        name="interview-report",
    ),
]