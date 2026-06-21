from django.db import models

from django.contrib.auth.models import User


class Interview(models.Model):
    """
    Model representing an interview session.
    Each interview is associated with a user and has a specific role and difficulty level.
    """

    ROLE_CHOICES = [
        ('python', 'Python Developer'),
        ('django', 'Django Developer'),
        ('fullstack', 'Full Stack Developer'),
        ('hr', 'HR Interview'),
    ]

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Returns a human-readable representation of the Interview object.
        This is displayed in the Django admin and when printing the object.
        """
        return f"{self.user.username} - {self.role}"


class Answer(models.Model):
    """
    Model representing a user's answer to an interview question.
    Each answer is associated with an interview and stores the question,
    the user's response, and the AI-generated evaluation.
    """

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.TextField()

    user_answer = models.TextField()

    score = models.IntegerField(
        null=True,
        blank=True
    )

    strengths = models.TextField(
        null=True,
        blank=True
    )

    weaknesses = models.TextField(
        null=True,
        blank=True
    )

    ideal_answer = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        """
        Returns a human-readable representation of the Answer object.
        Displays the question text for easy identification.
        """
        return self.question