from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from interviews.models import Interview
from interviews.models import Answer


class DashboardStatsView(APIView):
    """
    API view for retrieving dashboard statistics for an authenticated user.
    Calculates and returns total interviews, total answers, and average score.
    
    This view requires user authentication and returns aggregated statistics
    specific to the logged-in user.
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):

        """
        Handle GET request to retrieve dashboard statistics for the current user.
        
        Returns:
            Response containing:
            - total_interviews: Total number of interviews created by the user
            - total_answers: Total number of answers submitted by the user
            - average_score: Average score of all submitted answers (0 if no answers)
        """
        
        
        user = request.user

        
        total_interviews = Interview.objects.filter(
            user=user  # Filter interviews only for the current user
        ).count()  # Count the number of matching interviews
        
        total_answers = Answer.objects.filter(
            interview__user=user  # Use double underscore (__) to follow the ForeignKey relationship

        ).count()  # Count the number of matching answers
        
        average_score_result = Answer.objects.filter(
            interview__user=user  # Filter answers only for the current user's interviews
        ).aggregate(
            avg_score=Avg('score')  # Calculate the average of the 'score' field
        )
        
        average_score = average_score_result['avg_score'] if average_score_result['avg_score'] is not None else 0
        
        dashboard_stats = {
            'total_interviews': total_interviews,  # Number of interviews created
            'total_answers': total_answers,        # Number of answers submitted
            'average_score': average_score,        # Average score of answers
        }
        
        return Response(dashboard_stats, status=200)


class InterviewReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, interview_id):

        try:
            interview = Interview.objects.get(
                id=interview_id,
                user=request.user
            )
        except Interview.DoesNotExist:
            return Response(
                {"error": "Interview not found or you don't have permission to access it"},
                status=404
            )
        except Exception:
            return Response(
                {"error": "Authentication required"},
                status=401
            )

        answers = Answer.objects.filter(interview=interview)

        total_answers = answers.count()

        average_score_result = answers.aggregate(
            avg_score=Avg('score')
        )

        average_score = (
            average_score_result['avg_score']
            if average_score_result['avg_score'] is not None
            else 0
        )

        answers_data = []

        for answer in answers:
            answers_data.append({
                'question': answer.question,
                'user_answer': answer.user_answer,
                'score': answer.score,
                'strengths': answer.strengths,
                'weaknesses': answer.weaknesses,
                'ideal_answer': answer.ideal_answer,
            })

        interview_report = {
            'interview_id': interview.id,
            'role': interview.role,
            'difficulty': interview.difficulty,
            'total_answers': total_answers,
            'average_score': average_score,
            'answers': answers_data,
        }

        return Response(interview_report, status=200)