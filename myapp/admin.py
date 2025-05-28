from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,
    UserProfile,
    University,
    UserUniversityMatch,
    UniversityRegistration,
    Course
)

# Customize User admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )

# Inline for User Profile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Inline for University Matches
class UserUniversityMatchInline(admin.TabularInline):
    model = UserUniversityMatch
    extra = 1
    verbose_name_plural = 'University Matches'

# Inline for Courses
class CourseInline(admin.TabularInline):
    model = Course
    extra = 1

# Register User with custom admin and inlines
@admin.register(User)
class UserProfileAdmin(CustomUserAdmin):
    inlines = [UserProfileInline, UserUniversityMatchInline]

# Register UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'degree', 'interests', 'study_country', 'exam_type', 'exam_score')
    search_fields = ('user__username', 'user__email', 'degree', 'interests', 'study_country')
    list_filter = ('degree', 'study_country', 'exam_type')

# Register University
@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('college_name', 'organization_type', 'year', 'graduation_rate')
    search_fields = ('college_name', 'address', 'majors')
    list_filter = ('organization_type', 'size', 'area')

# Register UserUniversityMatch
@admin.register(UserUniversityMatch)
class UserUniversityMatchAdmin(admin.ModelAdmin):
    list_display = (
    'user', 'university_name', 'match_score', 'tuition_fee')  # ✅ Use 'university_name' instead of 'university'
    list_filter = ('university_name',)  # ✅ Use 'university_name' instead of 'university'
    search_fields = ('university_name', 'user__username')

# Register UniversityRegistration with CourseInline
@admin.register(UniversityRegistration)
class UniversityRegistrationAdmin(admin.ModelAdmin):
    list_display = ("university_name", "country", "state", "city")
    search_fields = ("university_name", "country", "state", "city")
    list_filter = ("country", "state")
    ordering = ("university_name",)
    inlines = [CourseInline]

# Register Course
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_name", "university", "cost", "totalseats", "closedate")
    search_fields = ("course_name", "university__university_name")
    list_filter = ("university", "closedate")
    ordering = ("university", "course_name")

    from django.contrib import admin
    from .models import College, UserApplication

    @admin.register(College)
    class CollegeAdmin(admin.ModelAdmin):
        """
        Admin configuration for College model
        """
        list_display = (
            'college_name',
            'address',
            'graduation_rate',
            'sat_score',
            'organization_type',
            'financial_aid',
            'area'
        )

        search_fields = ('college_name', 'address', 'area')

        list_filter = (
            'organization_type',
            'financial_aid',
            'area'
        )

    @admin.register(UserApplication)
    class UserApplicationAdmin(admin.ModelAdmin):
        """
        Admin configuration for UserApplication model
        """
        list_display = (
            'user',
            'college',
            'application_date',
            'status'
        )

        list_filter = (
            'status',
            'application_date'
        )

        search_fields = (
            'user__username',
            'college__college_name'
        )

        readonly_fields = ('application_date',)

        def get_queryset(self, request):
            """
            Optimize the queryset to reduce database queries
            """
            return super().get_queryset(request).select_related('user', 'college')


from .models import UserAnalysisDB

@admin.register(UserAnalysisDB)
class UserAnalysisDBAdmin(admin.ModelAdmin):
    list_display = ("name", "classification", "avg_cgpa", "sat_score_received", "created_at")
    search_fields = ("name", "classification", "skills", "extra_curricular", "competition_name")
    list_filter = ("classification", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {"fields": ("name", "classification")}),
        ("Academic Details", {
            "fields": ("tenth_marks_received", "tenth_marks_total", "twelfth_marks_received", "twelfth_marks_total",
                       "sat_score_received", "sat_score_total", "other_exam_score")
        }),
        ("College Details", {"fields": ("avg_cgpa", "competition_name", "learning_experience")}),
        ("Extra Curricular & Skills", {"fields": ("extra_curricular", "skills")}),
        ("Metadata", {"fields": ("created_at", "updated_at")}),
    )