from django import forms
from .models import User, UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['degree', 'interests', 'study_country', 'exam_type', 'exam_score', 'resume', 'additional_info']


from django import forms
from .models import UserAnalysisDB

class UserAnalysisForm(forms.ModelForm):
    class Meta:
        model = UserAnalysisDB
        exclude = ['classification', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tenth_marks_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tenth_marks_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'twelfth_marks_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'twelfth_marks_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sat_score_received': forms.NumberInput(attrs={'class': 'form-control'}),
            'sat_score_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'other_exam_score': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avg_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'competition_name': forms.TextInput(attrs={'class': 'form-control'}),
            'learning_experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'extra_curricular': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }