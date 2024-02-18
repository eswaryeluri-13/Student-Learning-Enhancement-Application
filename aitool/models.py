from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    SKILL_CHOICES = [
        ('C', 'C'),
        ('C++', 'C++'),
        ('Java', 'Java'),
        ('Python', 'Python'),
        ('JavaScript', 'JavaScript'),
        ('React', 'React'),
        ('R', 'R'),
        ('Haskell', 'Haskell'),
        ('SQL', 'SQL'),
        ('HTML_CSS', 'HTML and CSS'),
        ('PHP', 'PHP'),
    ]

    INTEREST_CHOICES = [
        ('Development', 'Development'),
        ('AI_ML', 'Artificial Intelligence and Machine Learning'),
        ('DBA', 'DBA (Database Administrator)'),
        ('Testing_Automation', 'Testing and Automation'),
        ('Research', 'Research Field'),
        ('UI_UX', 'UI/UX Designer'),
        ('Cyber_Security', 'Cyber Security Engineer'),
        ('IoT', 'Internet of Things (IOT)'),
        ('Data_Mining', 'Data Mining'),
        ('Data_Science', 'Data Science'),
    ]
    email_regex = RegexValidator(
        regex=r'^[a-zA-Z0-9_.+-]+@(gmail\.com|yahoo\.com)$',
        message="Email must be a valid Gmail or Yahoo address.",
    )
    
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField(default='default@example.com', validators=[email_regex])
    dob = models.DateField()
    education = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    skills = models.CharField(max_length=200, choices=SKILL_CHOICES, blank=True, null=True)
    interests = models.CharField(max_length=200, choices=INTEREST_CHOICES, blank=True, null=True)
    university = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    
    def __str__(self):
        return f"{self.username} - {self.dob.strftime('%Y-%m-%d')}"
    

'''class LoginForm(models.Model):
    username = models.CharField(max_length=50, required=True)
    password = models.CharField(widget=PasswordInput(), required=True)
    accept_terms = models.BooleanField(required=True)'''

    
