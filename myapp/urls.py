# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('university-signup/', views.university_signup, name='university_signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('register/', views.user_registration, name='register'),
    path('university/', views.university_recommendations, name='university_recommendations'),
    path('logout/', views.user_logout, name='logout'),
    path('dorai/', views.ai, name='dorai'),
    path('analysis/',views.profile_analyzer,name='analysis'),
    path('send-booking-email/', views.send_booking_email, name='send_booking_email'),
path('user-analysis/', views.user_analysis, name='user_analysis'),#ivleague
    path('analysis-result/<int:pk>/', views.analysis_result, name='analysis_result'),
    path('colleges/', views.colleges, name='colleges'),
    path('filter-universities/', views.filter_universities, name='filter-universities'),
    path('university-dashboard/<int:university_id>/', views.university_dashboard, name='university_dashboard'),
    path('university/<int:university_id>/add-courses/', views.add_courses, name='add_courses'),
    path('book-university/', views.book_university, name='book_university'),
    path('manage-applications/', views.manage_applications, name='manage_applications'),
    path('cancel-application/', views.cancel_application, name='cancel_application'),
    path('clean-sat-scores/', views.clean_sat_scores, name='clean_sat_scores'),
path('remove-application/<int:application_id>/', views.remove_application, name='remove_application'),
path('add-application/', views.add_application, name='add_application'),
    path('guidence/', views.guidence, name='guidence'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
        path('complete_profile',views.complete_profile,name='complete_profile'),

    # URL to remove a specific application
    # path('remove-application/<int:application_id>/',
    #      views.remove_application,
    #      name='remove_application'),
]
# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = '.views.custom_404'
