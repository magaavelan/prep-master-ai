from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Interview, Answer
from .serializers import InterviewSerializer, AnswerSerializer
from .question_bank import QUESTIONS
from .ai_service import evaluate_answer



class InterviewCreateView(APIView):
    """
    API view for creating a new interview session.
    Requires authentication - only logged-in users can create interviews.
    """
    
    permission_classes = [IsAuthenticated]


    def post(self, request):
        """
        Handle POST request to create a new interview.
        Validates data using serializer and associates interview with current user.
        """
        serializer = InterviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class InterviewListView(APIView):
    """
    API view for listing all interviews belonging to the authenticated user.
    Requires authentication - users can only see their own interviews.
    """
    
    permission_classes = [IsAuthenticated]


    def get(self, request):
        """
        Handle GET request to retrieve all interviews for the current user.
        Returns a serialized list of interview objects.
        """
        interviews = Interview.objects.filter(user=request.user)

        serializer = InterviewSerializer(
            interviews,
            many=True  # Serialize multiple objects
        )

        return Response(serializer.data)


class InterviewQuestionsView(APIView):
    
    permission_classes = [AllowAny]


    def get(self, request, interview_id):
        
        try:
            interview = Interview.objects.get(
                id=interview_id,
                user=request.user
            )
        except Interview.DoesNotExist:
            return Response(
                {"error": "Interview not found"}, 
                status=404
            )
        except Exception as e:
            return Response(
                {"error": "Authentication required"}, 
                status=401
            )

        questions = QUESTIONS.get(
            interview.role,  # Get questions for this role (e.g., 'python', 'django')
            {}  # Return empty dict if role not found
        ).get(
            interview.difficulty,  # Get questions for this difficulty level
            []  # Return empty list if difficulty not found
        )

        return Response({
            "interview_id": interview.id,
            "role": interview.role,
            "difficulty": interview.difficulty,
            "questions": questions
        })


class SubmitAnswerView(APIView):
    
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
       
        interview_id = request.data.get('interview_id')
        question = request.data.get('question')
        user_answer = request.data.get('user_answer')
        
        if not interview_id or not question or not user_answer:
            return Response(
                {"error": "Missing required fields: interview_id, question, user_answer"},
                status=400
            )
        
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
        
        answer = Answer(
            interview=interview,
            question=question,
            user_answer=user_answer
        )
        
        evaluation = evaluate_answer(question, user_answer)
        
        if evaluation is not None:
            answer.score = evaluation.get('score')
            
            answer.strengths = evaluation.get('strengths')
            
            answer.weaknesses = evaluation.get('weaknesses')
            
            answer.ideal_answer = evaluation.get('ideal_answer')
        else:
            
            answer.score = 5
            
            answer.strengths = "Evaluation unavailable - please try again later"
            
            answer.weaknesses = "Evaluation unavailable - please try again later"
            
            answer.ideal_answer = "Ideal answer unavailable - please try again later"
        
        answer.save()
        
        serializer = AnswerSerializer(answer)
        
        return Response(serializer.data, status=201)


class AnswerListView(APIView):
    
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
       
        
        user_interviews = Interview.objects.filter(user=request.user)
        
        answers = Answer.objects.filter(interview__in=user_interviews)
        
        answers = answers.order_by('-created_at')
        
        serializer = AnswerSerializer(answers, many=True)
        
        return Response(serializer.data)