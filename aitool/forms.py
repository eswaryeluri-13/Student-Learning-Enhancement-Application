# forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import UserProfile

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'name', 'dob', 'education', 'specialization', 'university', 'email']
        widgets = {
            'password': forms.PasswordInput(),
            'dob': forms.DateInput(attrs={'type': 'date'}),
        }

    skills = forms.MultipleChoiceField(choices=UserProfile.SKILL_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)
    interests = forms.MultipleChoiceField(choices=UserProfile.INTEREST_CHOICES, widget=forms.CheckboxSelectMultiple, required=False)

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        return ",".join(skills) if skills else None

    def clean_interests(self):
        interests = self.cleaned_data.get('interests')
        return ",".join(interests) if interests else None

    def clean(self):
        cleaned_data = super().clean()
        # Ensure that skills and interests are saved in the model fields
        cleaned_data['skills'] = cleaned_data.get('skills')
        cleaned_data['interests'] = cleaned_data.get('interests')
        return cleaned_data
    
    email_regex = RegexValidator(
        regex=r'^[a-zA-Z0-9_.+-]+@(gmail\.com|yahoo\.com|srmap\.edu\.in)$',
        message="Email must be a valid Gmail or Yahoo address or SRMAP Gmail address.",
    )
    email = forms.EmailField(validators=[email_regex])


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    
