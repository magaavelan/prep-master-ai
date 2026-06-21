from django.shortcuts import render, redirect
from django.views import View


class TemplatePageView(View):
    template_name: str

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class LoginPageView(TemplatePageView):
    template_name = "login.html"


class HistoryDashboardPageView(TemplatePageView):
    template_name = "history_dashboard.html"


# Renamed to HomePageView to serve home.html after login
class HomePageView(TemplatePageView):
    template_name = "home.html"


class InterviewSessionPageView(TemplatePageView):
    template_name = "interviewsession.html"


class InterviewReportPageView(TemplatePageView):
    template_name = "interview_report.html"


class InterviewSetupPageView(TemplatePageView):
    template_name = "interviewsetuppage.html"

    def post(self, request, *args, **kwargs):
        return redirect("/interview/session/")