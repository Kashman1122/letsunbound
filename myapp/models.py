# models.py
from django.db import models
from django.conf import settings

from django.contrib.auth.models import User

class UniversityRegistration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="university")
    university_name = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    location = models.CharField(max_length=255, blank=True, null=True)
    offered_courses = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.university_name


class UserAnalysisDB(models.Model):
    # Basic Information
    name = models.CharField(max_length=100)

    # Academic Details
    tenth_marks_received = models.FloatField()
    tenth_marks_total = models.FloatField(default=100)
    twelfth_marks_received = models.FloatField()
    twelfth_marks_total = models.FloatField(default=100)
    sat_score_received = models.IntegerField(null=True, blank=True)
    sat_score_total = models.IntegerField(default=1600, null=True, blank=True)
    other_exam_score = models.TextField(null=True, blank=True)

    # College Details (Not Mandatory)
    avg_cgpa = models.FloatField(null=True, blank=True)
    competition_name = models.CharField(max_length=200, null=True, blank=True)
    learning_experience = models.TextField(null=True, blank=True)

    # Extra Curricular Activities (Not Mandatory)
    extra_curricular = models.TextField(null=True, blank=True)

    # Skills
    skills = models.TextField(null=True, blank=True)

    # Classification
    classification = models.CharField(max_length=10, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.classification or 'Unclassified'}"

class Course(models.Model):
    university = models.ForeignKey(
        UniversityRegistration,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    course_name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    totalseats = models.PositiveIntegerField()
    closedate = models.DateTimeField()

    def __str__(self):
        return f"{self.course_name} - {self.university.university_name}"


from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # Add these custom related_name attributes
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    degree = models.CharField(max_length=50, blank=True, null=True)
    interests = models.CharField(max_length=50, blank=True, null=True)
    study_country = models.CharField(max_length=50, blank=True, null=True)
    exam_type = models.CharField(max_length=50, blank=True, null=True)
    exam_score = models.FloatField(default=0.0, blank=True, null=True)
    resume = models.FileField(upload_to='resumes/resumes', blank=True, null=True)
    additional_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def is_complete(self):
        """Check if the profile has all required information for university matching"""
        return all([
            self.degree,
            self.interests,
            self.study_country,
            self.exam_type
        ])


# class University(models.Model):
#     college_name = models.CharField(max_length=255)
#     address = models.TextField()
#     year = models.CharField(max_length=100, null=True, blank=True)  # Changed to CharField to accept strings like "4-year"
#     organization_type = models.CharField(max_length=100, null=True, blank=True)
#     size = models.CharField(max_length=100, null=True, blank=True)
#     area = models.CharField(max_length=100, null=True, blank=True)
#     graduation_rate = models.FloatField(null=True, blank=True)
#     financial_aid = models.FloatField(null=True, blank=True)
#     sat_score = models.IntegerField(null=True, blank=True)
#     majors = models.TextField(null=True, blank=True)
#
#     def __str__(self):
#         return self.college_name
#
#     class Meta:
#         verbose_name_plural = "Universities"
class University(models.Model):
    college_name = models.CharField(max_length=255)
    address = models.TextField()
    year = models.CharField(max_length=100, null=True, blank=True)  # "4-year"
    organization_type = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    graduation_rate = models.CharField(max_length=20, null=True, blank=True)  # "42%"
    financial_aid = models.CharField(max_length=50, null=True, blank=True)  # "$6K"
    sat_score = models.CharField(max_length=20, null=True, blank=True)  # "422-546"
    net_price = models.CharField(max_length=50, null=True, blank=True)  # "$6K"
    majors = models.TextField(null=True, blank=True)
    rank = models.IntegerField(null=True, blank=True)
    # Add new fields
    logo_url = models.URLField(max_length=500, null=True, blank=True)  # For University Logo 1
    logo2_url = models.URLField(max_length=500, null=True, blank=True)  # For University Logo 2
    university_url = models.URLField(max_length=500, null=True, blank=True)  # For official University URL

    def __str__(self):
        return self.college_name

    class Meta:
        verbose_name_plural = "Universities"

class UserUniversityMatch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=255)  # ✅ Ensure this exists
    university_url = models.URLField(blank=True, null=True)
    match_score = models.FloatField(default=0)
    tuition_fee = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    address = models.CharField(max_length=255, blank=True, null=True)  # ✅ Added address
    area = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added area
    financial_aid = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added financial aid
    graduation_rate = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added graduation rate
    organization_type = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added organization type
    sat_score = models.CharField(max_length=100, blank=True, null=True)  # ✅ Added SAT score
    year = models.CharField(max_length=50, blank=True, null=True)  # ✅ Added year field

    def __str__(self):
        return f"{self.university_name} - {self.user.username}"  # ✅ Ensure correct return

class College(models.Model):
    """
    Model to store college information
    """
    college_name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    graduation_rate = models.FloatField()
    sat_score = models.IntegerField()
    organization_type = models.CharField(max_length=100)
    financial_aid = models.BooleanField(default=False)
    area = models.CharField(max_length=100)

    def __str__(self):
        return self.college_name

from django.utils.translation import gettext_lazy as _

class UserApplication(models.Model):
    """
    Model to track user's university applications
    """
    STATUS_CHOICES = [
        ('APPLIED', _('Applied')),
        ('IN_REVIEW', _('In Review')),
        ('ACCEPTED', _('Accepted')),
        ('REJECTED', _('Rejected')),
        ('WAITLISTED', _('Waitlisted'))
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='university_applications'
    )
    college = models.ForeignKey(
        College,
        on_delete=models.CASCADE,
        related_name='applicant_set'
    )
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='APPLIED'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Additional Notes')
    )

    class Meta:
        unique_together = ('user', 'college')
        verbose_name = _('University Application')
        verbose_name_plural = _('University Applications')
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.college.college_name}"