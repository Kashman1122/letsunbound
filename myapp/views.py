# views.py
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UniversityRegistration, Course
from pymongo import MongoClient
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, UserProfile, University, UserUniversityMatch
from .forms import UserRegistrationForm, UserProfileForm
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, UserProfile, UserUniversityMatch
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings #vector embeding technique
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_groq import ChatGroq
from django.core.validators import validate_email
from dotenv import load_dotenv
import os
from django.http import JsonResponse
from django.http import JsonResponse
import csv
from django.core.mail import send_mail
import io
import json
from .models import College, UserApplication
import re
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.http import JsonResponse

def index(request):
    return render(request, 'index.html')

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def send_booking_email(request):
    if request.method == "POST":
        # Get data from POST request
        user_email = request.POST.get('email')
        university_name = request.POST.get('university_name')
        area = request.POST.get('area')
        graduation_rate = request.POST.get('graduation_rate')
        organization_type = request.POST.get('organization_type')
        financial_aid = request.POST.get('financial_aid')

        # Construct the email message
        subject = f"Booking Confirmation for {university_name}"
        message = f"""
        Hello,

        You have successfully booked a seat at {university_name} in the {area} area.

        Details:
        - Graduation Rate: {graduation_rate}
        - Organization Type: {organization_type}
        - Financial Aid: {financial_aid}

        Best regards,
        Your Booking Team
        """
        from_email = settings.DEFAULT_FROM_EMAIL

        # Send the email
        send_mail(subject, message, from_email, [user_email])

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

def university_signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # University details
        uniname = request.POST.get('uniname')
        unicountry = request.POST.get('unicountry')
        unistate = request.POST.get('unistate')
        unicity = request.POST.get('unicity')
        unilocation = request.POST.get('unilocation')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, 'university_registration.html')

        # Create user account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create university profile
        university = UniversityRegistration.objects.create(
            user=user,
            university_name=uniname,
            country=unicountry,
            state=unistate,
            city=unicity,
            location=unilocation
        )

        # Log the user in
        login(request, user)

        messages.success(request, f"University '{uniname}' registered successfully! You can now add courses.")
        return redirect('university_dashboard', university_id=university.id)

    return render(request, 'university_registration.html')


def signin(request):
    if request.method == 'POST':
        try:
            uname = request.POST.get('username')
            password = request.POST.get('password')


            # Django authentication expects username, but we're using email as username
            user = authenticate(request, username=uname, password=password)

            if user is not None:
                login(request, user)

                # Check if user has matches to display recommendations
                if UserUniversityMatch.objects.filter(user=user).exists():
                    return redirect('university_recommendations')
                else:
                    # If no matches yet, could redirect to profile completion or elsewhere
                    return redirect('complete_profile')
            else:
                return JsonResponse({'error': 'Invalid email or password'}, status=401)

        except Exception as e:
            print("Error in user_signin:", str(e))
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return render(request, 'signin.html')


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('index')


@login_required
def university_dashboard(request, university_id):
    university = get_object_or_404(UniversityRegistration, id=university_id)

    # Ensure the user can only access their own university dashboard
    if request.user != university.user:
        messages.error(request, "You don't have permission to view this dashboard.")
        return redirect('index')

    courses = university.courses.all()
    return render(request, 'university_dashboard.html', {'university': university, 'courses': courses})


@login_required
def add_courses(request, university_id):
    university = get_object_or_404(UniversityRegistration, id=university_id)

    # Ensure the user can only add courses to their own university
    if request.user != university.user:
        messages.error(request, "You don't have permission to add courses to this university.")
        return redirect('index')

    if request.method == "POST":
        courses = request.POST.getlist('course_name[]')
        costs = request.POST.getlist('cost[]')
        seats = request.POST.getlist('totalseats[]')
        closedates = request.POST.getlist('closedate[]')

        courses_added = 0
        for i in range(len(courses)):
            if courses[i]:  # Ensure the course name is provided
                Course.objects.create(
                    university=university,
                    course_name=courses[i],
                    cost=costs[i],
                    totalseats=seats[i],
                    closedate=closedates[i]
                )
                courses_added += 1

        messages.success(request, f"Added {courses_added} new courses to '{university.university_name}'!")
        return redirect('university_dashboard', university_id=university.id)

    return render(request, 'add_courses.html', {'university': university})




# Fetch university data from URL
def fetch_university_data():
    url = "https://raw.githubusercontent.com/Hipo/university-domains-list/refs/heads/master/world_universities_and_domains.json"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else []


# Convert university data into vector database
def create_vector_db():
    university_data = fetch_university_data()
    documents = []

    for uni in university_data:
        doc_text = f"{uni['name']}, {uni['country']}, {uni.get('state-province', '')}. Website: {', '.join(uni['web_pages'])}"
        documents.append(Document(page_content=doc_text, metadata=uni))

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001",google_api_key=api_key)
    vector_db = FAISS.from_documents(documents, embeddings)
    return vector_db


# Initialize vector database
# VECTOR_DB = create_vector_db()

def user_registration(request):
    if request.method == 'POST':
        try:
            form_data = request.POST

            # Validate required fields for basic registration
            required_fields = ['email', 'password', 'name', 'phone']
            for field in required_fields:
                if not form_data.get(field):
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Check if passwords match
            if form_data.get('password') != form_data.get('confirmPassword'):
                return JsonResponse({'error': 'Passwords do not match'}, status=400)

            # Check if user already exists
            if User.objects.filter(email=form_data.get('email')).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=400)

            user = User.objects.create_user(
                username=form_data.get('email'),
                email=form_data.get('email'),
                password=form_data.get('password'),
                first_name=form_data.get('name').split()[0],
                last_name=' '.join(form_data.get('name').split()[1:]) if len(form_data.get('name').split()) > 1 else '',
            )

            # Create UserProfile with only basic info, rest as null/default
            profile = UserProfile.objects.create(
                user=user,
                phone_number=form_data.get('phone', ''),
                degree='',  # Will be filled later
                interests='',  # Will be filled later
                study_country='',  # Will be filled later
                exam_type='',  # Will be filled later
                exam_score=0.0,  # Will be filled later
                additional_info=''  # Will be filled later
            )

            login(request, user)
            return redirect('university_recommendations')

        except Exception as e:
            print("Error in user_registration:", str(e))
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return render(request, 'registration.html')


def complete_profile(request):
    if request.method == 'POST':
        try:
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'User not authenticated'}, status=401)

            form_data = request.POST
            file_data = request.FILES

            # Validate required fields for profile completion
            required_fields = ['degree', 'interests', 'country', 'exam']
            for field in required_fields:
                if not form_data.get(field):
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Update user profile
            profile = request.user.profile
            profile.degree = form_data.get('degree')
            profile.interests = form_data.get('interests')
            profile.study_country = form_data.get('country')
            profile.exam_type = form_data.get('exam')

            # Get exam score based on exam type
            exam_type = form_data.get('exam')
            exam_score = float(form_data.get(f"{exam_type}Marks", 0))
            profile.exam_score = exam_score

            if file_data.get('profilePdf'):
                profile.resume = file_data.get('profilePdf')

            profile.additional_info = form_data.get('additionalInfo', '')
            profile.save()

            # Get university matches after profile completion
            university_matches = get_university_matches(profile)

            # Clear existing matches and create new ones
            UserUniversityMatch.objects.filter(user=request.user).delete()

            for match in university_matches:
                UserUniversityMatch.objects.create(
                    user=request.user,
                    university_name=match['college_name'],
                    university_url=match['university_url'] or '',
                    match_score=match['match_score'],
                    tuition_fee=match['net_price'] or 'N/A',
                    description=f"Located in {match['area']}. {match['majors'][:100] if match['majors'] else 'No major details available.'}...",
                    address=match['address'],
                    area=match['area'] or 'Unknown',
                    financial_aid=match['financial_aid'] or 'Unknown',
                    graduation_rate=match['graduation_rate'] or 'Unknown',
                    organization_type=match['organization_type'] or 'Unknown',
                    sat_score=match['sat_score'] or 'Unknown',
                    year=match['year'] or 'Unknown'
                )

            return JsonResponse({'success': True, 'message': 'Profile completed successfully'})

        except Exception as e:
            print("Error in complete_profile:", str(e))
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def university_recommendations(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Check if profile is complete
    profile = request.user.profile
    profile_complete = all([
        profile.degree,
        profile.interests,
        profile.study_country,
        profile.exam_type
    ])

    matches = []
    if profile_complete:
        matches = UserUniversityMatch.objects.filter(user=request.user)

    context = {
        'matches': matches,
        'profile_complete': profile_complete,
        'user': request.user
    }

    return render(request, 'university.html', context)


def get_university_matches(profile):
    """
    Find universities that match user's interests and study country
    """
    from django.db.models import Q, Case, When, IntegerField

    user_interests = profile.interests.lower().split(',')
    user_interests = [interest.strip() for interest in user_interests]
    study_country = profile.study_country.lower()

    # Build query for matching universities
    interest_queries = Q()
    for interest in user_interests:
        # Match interests in majors field (case-insensitive)
        interest_queries |= Q(majors__icontains=interest)

    # Country matching in area field
    country_query = Q(area__icontains=study_country)

    # Get universities that match either interests or country (or both)
    universities = University.objects.filter(
        interest_queries | country_query
    ).annotate(
        # Calculate match score based on matches
        match_score=Case(
            # Both interests and country match - highest score
            When(Q(majors__icontains=user_interests[0]) & Q(area__icontains=study_country), then=95),
            # Multiple interests match
            When(interest_queries & Q(area__icontains=study_country), then=90),
            # One interest + country match
            When(interest_queries, then=85),
            # Only country match
            When(country_query, then=75),
            # Default score
            default=70,
            output_field=IntegerField()
        )
    ).order_by('-match_score', '-rank')[:20]  # Limit to top 20 matches

    # Convert to list of dictionaries for compatibility
    matches = []
    for university in universities:
        # Calculate more precise match score
        precise_score = calculate_precise_match_score(university, user_interests, study_country)

        matches.append({
            'college_name': university.college_name,
            'address': university.address,
            'year': university.year,
            'organization_type': university.organization_type,
            'size': university.size,
            'area': university.area,
            'graduation_rate': university.graduation_rate,
            'financial_aid': university.financial_aid,
            'sat_score': university.sat_score,
            'net_price': university.net_price,
            'majors': university.majors,
            'rank': university.rank,
            'logo_url': university.logo_url,
            'logo2_url': university.logo2_url,
            'university_url': university.university_url,
            'match_score': precise_score
        })

    return matches


def calculate_precise_match_score(university, user_interests, study_country):
    """
    Calculate a more precise match score based on multiple factors
    """
    score = 0

    # Base score
    base_score = 50

    # Interest matching (40 points max)
    interest_score = 0
    if university.majors:
        majors_lower = university.majors.lower()
        matched_interests = 0
        for interest in user_interests:
            if interest in majors_lower:
                matched_interests += 1

        if matched_interests > 0:
            interest_score = min(40, (matched_interests / len(user_interests)) * 40)

    # Country/Area matching (30 points max)
    area_score = 0
    if university.area and study_country in university.area.lower():
        area_score = 30

    # Ranking bonus (10 points max)
    rank_score = 0
    if university.rank:
        if university.rank <= 50:
            rank_score = 10
        elif university.rank <= 100:
            rank_score = 7
        elif university.rank <= 200:
            rank_score = 5
        else:
            rank_score = 2

    # Graduation rate bonus (10 points max)
    grad_rate_score = 0
    if university.graduation_rate:
        try:
            rate = float(university.graduation_rate.replace('%', ''))
            if rate >= 80:
                grad_rate_score = 10
            elif rate >= 70:
                grad_rate_score = 7
            elif rate >= 60:
                grad_rate_score = 5
            else:
                grad_rate_score = 2
        except (ValueError, AttributeError):
            grad_rate_score = 0

    # Financial aid bonus (10 points max)
    aid_score = 0
    if university.financial_aid and university.financial_aid != 'Unknown':
        aid_score = 5

    total_score = base_score + interest_score + area_score + rank_score + grad_rate_score + aid_score
    return min(100, int(total_score))

import json

def connect_to_mongodb():
    """
    Establish connection to MongoDB Atlas

    Returns:
        Tuple of (client, database, collection)
    """
    try:
        connection_string = "mongodb+srv://letsunbound:test123@cluster0.iz8ovwj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(connection_string)
        db = client['university_database']
        collection = db['university_vectors']
        return client, db, collection
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None, None, None


def text_search(query_text):
    """
    Perform a full-text search on the university database with filtering by country and degree.

    Args:
        query_text (str): Search query.

    Returns:
        List of matching university documents.
    """
    client, _, collection = connect_to_mongodb()
    if collection is None:
        return []

    query_parts = query_text.split(",")
    country_name = query_parts[-1].strip() if query_parts else ""

    pipeline = [
        {
            "$search": {
                "index": "university_index",
                "compound": {
                    "should": [
                        {
                            "text": {
                                "query": query_text,
                                "path": {
                                    "wildcard": "*"
                                },
                                "score": {"boost": {"value": 2}}
                            }
                        },
                        {
                            "text": {
                                "query": country_name,
                                "path": "country",
                                "score": {"boost": {"value": 10}}
                            }
                        }
                    ],
                    "minimumShouldMatch": 1
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "college_name": 1,
                "country": 1,
                "address": 1,
                "area": 1,
                "financial_aid": 1,
                "graduation_rate": 1,
                "year": 1,
                "sat_score": 1,
                "organization_type": 1,
                "similarity_score": {"$meta": "searchScore"}
            }
        },
        {
            "$sort": {"similarity_score": -1}
        }
    ]

    results = list(collection.aggregate(pipeline))
    client.close()
    return results


def analyzer(user_profile):
    """
    Analyze the user profile and return a list of matching universities from MongoDB.

    Args:
        user_profile: Object containing user preferences (degree, interests, study_country).

    Returns:
        List of matching university documents.
    """
    query_text = f"{user_profile.degree}, {user_profile.interests}, {user_profile.study_country}"
    print(f"Searching with query: {query_text}")

    matched_universities = text_search(query_text)

    if not matched_universities:
        return [{"name": "N/A", "country": "N/A", "web_pages": [], "cost": "N/A",
                 "details": "No matching universities found."}]

    return matched_universities

from django.db.models import Avg


# views.py
@login_required
def profile_analyzer(request):
    user = request.user

    # Handle form submission for resume upload
    if request.method == 'POST' and request.FILES.get('resume'):
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.resume:
                profile.resume.delete(save=False)
            profile.resume = request.FILES['resume']
            profile.save()
            messages.success(request, "Resume updated successfully!")
            return redirect('analysis')
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user, resume=request.FILES['resume'])
            profile.save()
            messages.success(request, "Resume uploaded successfully!")
            return redirect('analysis')

    try:
        profile = UserProfile.objects.get(user=user)
        resume_url = profile.resume.url if profile.resume else None
    except UserProfile.DoesNotExist:
        profile = None
        resume_url = None

    avg_match_score = UserUniversityMatch.objects.filter(user=user).aggregate(Avg('match_score'))['match_score__avg']

    # Fetch classification result
    try:
        user_analysis = UserAnalysisDB.objects.get(name=user.username)  # Assuming username is the key
        classification = user_analysis.classification
    except UserAnalysisDB.DoesNotExist:
        classification = "Not Classified"

    context = {
        'profile': profile,
        'resume_url': resume_url,
        'avg_match_score': avg_match_score if avg_match_score is not None else 0,
        'classification': classification,
    }

    return render(request, 'profile_analysis.html', context)



# @login_required
# def university_recommendations(request):
#     matches = UserUniversityMatch.objects.filter(user=request.user).order_by('-match_score')
#     return render(request, 'university.html', {'matches': matches})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


import os
import openai
from django.http import JsonResponse
from django.shortcuts import render

import openai
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import openai
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # Add this if you're having CSRF issues
def ai(request):
    if request.method == "POST":
        query = request.POST.get('user_query')
        # Check if query exists
        if not query:
            error_message = "No query provided"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_message}, status=400)
            return render(request, 'ai.html', {'error': error_message})
        try:
            # Set your OpenAI API key directly (NOT RECOMMENDED FOR PRODUCTION)
            api_key = os.getenv("OPENAI_API_KEY")

            # Define the system prompt to limit responses to colleges only
            system_prompt = """You are a specialized college information assistant. Your role is to help users with college-related queries ONLY.

WHAT YOU CAN HELP WITH:
- College admissions information
- Course details and curriculum
- Campus facilities and student life
- Fees and scholarships
- Placement opportunities
- Career guidance related to college education
- Entrance exam information
- College comparisons and rankings
- Academic programs and departments
- Student support services

IMPORTANT RULES:
1. ONLY answer questions related to colleges, universities, and higher education
2. If asked about anything unrelated to colleges (like cooking, sports, movies, weather, etc.), respond with: "Sorry, I am specifically trained to assist with college-related queries only. Please ask me about colleges, admissions, courses, or anything related to higher education."
3. If asked about who developed you or who your developer is, respond with: "I was developed by LetsUnbound team to help students with college-related information."
4. Stay focused on providing helpful, accurate information about colleges and higher education
5. Be friendly and helpful within your area of expertise

Please respond to the user's query keeping these guidelines in mind."""

            # For OpenAI library v1.x+ (current version)
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",  # Use valid model name
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,  # Slightly lower temperature for more focused responses
                max_tokens=5000,   # Limit response length
            )
            response_text = response.choices[0].message.content

            # Return JSON response for AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'response': response_text})
            # If not AJAX, return with context (fallback)
            return render(request, 'ai.html', {'response': response_text, 'query': query})
        except Exception as e:
            # Handle errors gracefully
            error_message = f"Error: {str(e)}"
            print(f"OpenAI API Error: {e}")  # Log for debugging
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_message}, status=500)
            return render(request, 'ai.html', {'error': error_message})
    # For GET requests, just render the template
    return render(request, 'ai.html')


@login_required
def filter_universities(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            country = data.get('country', '')
            degree = data.get('degree', '')

            # Get the logged-in user's profile
            user = request.user
            profile = UserProfile.objects.get(user=user)

            # Update the profile's study_country & degree
            profile.study_country = country
            profile.degree = degree
            profile.save()

            # Fetch new matching universities
            matched_universities = text_search(f"{degree}, {country}")

            # Remove previous matches and add new ones
            UserUniversityMatch.objects.filter(user=user).delete()

            for match in matched_universities:
                UserUniversityMatch.objects.create(
                    user=user,
                    university_name=match.get('college_name', 'Unknown University'),
                    university_url=match.get('web_pages', ''),
                    match_score=match.get('similarity_score', 0),
                    tuition_fee=match.get('tuition_cost', 'N/A'),
                    description=match.get('description', 'No details available.'),
                    address=match.get('address', 'Unknown'),
                    area=match.get('area', 'Unknown'),
                    financial_aid=match.get('financial_aid', 'Unknown'),
                    graduation_rate=match.get('graduation_rate', 'Unknown'),
                    organization_type=match.get('organization_type', 'Unknown'),
                    sat_score=match.get('sat_score', 'Unknown'),
                    year=match.get('year', 'Unknown')
                )

            return JsonResponse({'universities': matched_universities})

        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
        except Exception as e:
            print("Error in filter_universities:", str(e))
            return JsonResponse({'error': 'Internal server error'}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# def colleges(request):
#     """
#     Connects to MongoDB, fetches data from 'university_vectors', and renders it in the template.
#     """
#     try:
#         connection_string = "mongodb+srv://letsunbound:test123@cluster0.iz8ovwj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
#         client = MongoClient(connection_string)
#         db = client['university_database']
#         collection = db['university_vectors']
#
#         data = list(collection.find())  # ✅ Fetch all documents
#         for item in data:
#             item["_id"] = str(item["_id"])  # Convert ObjectId to string for rendering
#
#         return render(request, 'colleges.html', {'colleges': data})
#
#     except Exception as e:
#         print(f"MongoDB Connection Error: {e}")
#
#     return render(request, 'colleges.html', {'colleges': []})  # Return empty list if an error occurs

logger = logging.getLogger(__name__)
@csrf_exempt
def colleges(request):
    """
    Fetches university data from SQLite database and renders it in the template.
    Also handles form submissions for college information requests.
    """
    if request.method == 'POST':
        try:
            # For form-data submissions
            if request.content_type and 'application/json' in request.content_type:
                # Handle JSON payload
                data = json.loads(request.body)
                logger.info(f"Received JSON data: {data}")
            else:
                # Handle form-data submission
                data = {
                    'user_name': request.POST.get('name'),
                    'user_email': request.POST.get('email'),
                    'phone': request.POST.get('phone', ''),
                    'college': {
                        'id': request.POST.get('college_id'),
                        'name': request.POST.get('college_name', 'Selected College')
                    }
                }
                logger.info(f"Received form data: {data}")

            user_name = data.get('user_name')
            user_email = data.get('user_email')
            phone = data.get('phone', '')
            college = data.get('college', {})
            college_id = college.get('id')
            college_name = college.get('name', 'the college you selected')
            validate_email(user_email)
            logger.info(f"Processing request for: {user_name}, {user_email}, college: {college_name}")

            if not user_name or not user_email:
                if 'application/json' in request.content_type:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Name and email are required'
                    }, status=400)
                else:
                    # Fetch all universities for the normal page render
                    universities = University.objects.all()
                    return render(request, 'colleges.html', {
                        'colleges': universities,
                        'error': 'Name and email are required'
                    })

            # Get college details from database if possible
            try:
                college_obj = University.objects.get(id=college_id)
                college_details = {
                    'name': college_obj.college_name,
                    'rank': college_obj.rank if hasattr(college_obj, 'rank') else 'N/A',
                    'sat': college_obj.sat_score if hasattr(college_obj, 'sat_score') else 'N/A',
                    'graduation_rate': college_obj.graduation_rate if hasattr(college_obj,
                                                                              'graduation_rate') else 'N/A',
                    'net_price': college_obj.net_price if hasattr(college_obj, 'net_price') else 'N/A'
                }
                college_name = college_obj.college_name
            except University.DoesNotExist:
                college_details = {
                    'name': college_name,
                    'rank': 'N/A',
                    'sat': 'N/A',
                    'graduation_rate': 'N/A',
                    'net_price': 'N/A'
                }
            except Exception as e:
                logger.error(f"Error retrieving college details: {str(e)}")
                college_details = {
                    'name': college_name,
                    'rank': 'N/A',
                    'sat': 'N/A',
                    'graduation_rate': 'N/A',
                    'net_price': 'N/A'
                }

            # Prepare thank-you email with college details
            subject = f"Information about {college_name} - LetsUnbound"
            message = f"""
            Dear {user_name},

            Thank you for choosing LetsUnbound!

            We have received your interest in the following college:

            College Name: {college_details['name']}
            Rank: {college_details['rank']}
            SAT Score: {college_details['sat']}
            Graduation Rate: {college_details['graduation_rate']}
            Net Price: {college_details['net_price']}

            Our team will contact you shortly with more detailed information about {college_details['name']}.

            If you have any questions in the meantime, please don't hesitate to reach out to us.

            Best regards,
            The LetsUnbound Team
            """

            try:
                # Send email directly without saving to database
                email_sent = send_mail(
                    subject,
                    message,
                    'letscrackwithunbound@gmail.com',  # FROM
                    [user_email],  # TO
                    fail_silently=False,
                )

                logger.info(f"Email sent successfully to {user_email}")

                # Also send notification to admin
                admin_subject = f"New College Information Request: {college_name}"
                admin_message = f"""
                A new college information request has been received:

                User: {user_name}
                Email: {user_email}
                Phone: {phone}
                College: {college_name} (ID: {college_id})

                An acknowledgment email has been sent to the user.
                """

                send_mail(
                    admin_subject,
                    admin_message,
                    'letscrackwithunbound@gmail.com',  # FROM
                    ['admin@letsunbound.com'],  # TO ADMIN
                    fail_silently=True,
                )

                if 'application/json' in request.content_type:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Thank-you email sent successfully'
                    })
                else:
                    # Fetch all universities for the normal page render
                    universities = University.objects.all()
                    return render(request, 'colleges.html', {
                        'colleges': universities,
                        'success': f'Thank you! Information has been sent to {user_email}'
                    })

            except Exception as e:
                logger.error(f"Failed to send email: {str(e)}")
                if 'application/json' in request.content_type:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Failed to send email: {str(e)}'
                    }, status=500)
                else:
                    # Fetch all universities for the normal page render
                    universities = University.objects.all()
                    return render(request, 'colleges.html', {
                        'colleges': universities,
                        'error': 'There was a problem sending your email. Please try again later.'
                    })

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid JSON data: {str(e)}'
            }, status=400)

        except Exception as e:
            logger.error(f"Unexpected error in colleges view: {str(e)}")
            if request.content_type and 'application/json' in request.content_type:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Server error: {str(e)}'
                }, status=500)
            else:
                # Fetch all universities for the normal page render
                universities = University.objects.all()
                return render(request, 'colleges.html', {
                    'colleges': universities,
                    'error': 'An unexpected error occurred. Please try again later.'
                })

    # For GET requests, show the normal colleges page
    try:
        # Fetch all university records from the database
        universities = University.objects.all()
        return render(request, 'colleges.html', {'colleges': universities})
    except Exception as e:
        logger.error(f"Database Error: {e}")
        return render(request, 'colleges.html', {'colleges': []})  # Return empty list if an error occurs


@csrf_protect
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a CSV file')
            return redirect('upload_sat_scores')

        try:
            # Read and decode the CSV
            csv_data = csv_file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_data))

            updated_count = 0
            not_found_count = 0
            skipped_count = 0

            for row in csv_reader:
                # Get university name and country from the CSV
                university_name = row.get('College Name', '').strip()
                country = row.get('country', '').strip()

                # Skip if university name or country is missing
                if not university_name or not country:
                    skipped_count += 1
                    continue

                # First try an exact match on college_name
                matching_universities = University.objects.filter(college_name__exact=university_name)

                # If no exact match is found, try a case-insensitive match
                if not matching_universities.exists():
                    matching_universities = University.objects.filter(college_name__iexact=university_name)

                # If we found matches, update them
                if matching_universities.exists():
                    for university in matching_universities:
                        # Check if country is already in the address
                        if country not in university.address:
                            # Append country to the existing address
                            if university.address:
                                # Only add a comma if the address doesn't already end with one
                                if university.address.strip().endswith(','):
                                    university.address = f"{university.address} {country}"
                                else:
                                    university.address = f"{university.address}, {country}"
                            else:
                                university.address = country

                            university.save()
                            updated_count += 1
                            print(f"Updated address for {university.college_name}: {university.address}")
                        else:
                            skipped_count += 1
                            print(f"Skipping {university.college_name} - Country already in address")
                else:
                    not_found_count += 1
                    print(f"No match found for '{university_name}'")

            # Prepare status message
            status_message = f'Updated addresses with country for {updated_count} universities. '
            if skipped_count > 0:
                status_message += f'{skipped_count} universities skipped (country already present or missing data). '
            if not_found_count > 0:
                status_message += f'{not_found_count} universities not found.'

            messages.success(request, status_message)
            return redirect('colleges')

        except Exception as e:
            messages.error(request, f'Error processing CSV file: {str(e)}')
            return redirect('upload_sat_scores')

    return render(request, 'upload_csv.html')


def clean_sat_scores(request):
    """
    Remove 'SAT range' text from SAT scores in the University database.
    Can be called via URL to clean existing SAT score entries.
    """
    # Track the number of universities updated
    updated_count = 0

    # Get all universities with SAT scores
    universities = University.objects.exclude(sat_score__isnull=True).exclude(sat_score='')

    for university in universities:
        # Check if SAT score contains 'SAT range' text
        original_sat_score = university.sat_score

        # Use regex to extract only the numeric SAT score range
        sat_match = re.search(r'(\d{3,4})-(\d{3,4})', original_sat_score)

        if sat_match:
            # Extract just the numeric range
            cleaned_sat_score = sat_match.group(0)

            # Only update if the extracted score is different from the original
            if cleaned_sat_score != original_sat_score:
                university.sat_score = cleaned_sat_score
                university.save()
                updated_count += 1
                print(f"Cleaned SAT score for {university.college_name}: {original_sat_score} → {cleaned_sat_score}")

    # Prepare and return a response
    if request.method == 'GET':
        # If accessed via URL, return a simple HttpResponse
        return HttpResponse(f"Cleaned SAT scores for {updated_count} universities.")

    # For potential future use with POST requests or other methods
    return redirect('colleges')


# @login_required
# def manage_applications(request):
#     """
#     View to display and manage user's university applications
#     """
#     user_applications = UserApplication.objects.filter(user=request.user)
#
#     context = {
#         'applications': user_applications,
#         'total_applications': user_applications.count(),
#         'accepted_applications': user_applications.filter(status='ACCEPTED').count(),
#         'pending_applications': user_applications.exclude(status='ACCEPTED').count()
#     }
#
#     return render(request, 'manage_applications.html', context)
#
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
#
#
# @login_required
# def add_application(request, college_id):
#     try:
#         # Find the college
#         college = College.objects.get(id=college_id)
#
#         # Check if application already exists
#         existing_application = UserApplication.objects.filter(
#             user=request.user,
#             college=college
#         ).first()
#
#         if existing_application:
#             messages.warning(request, f'You have already applied to {college.college_name}.')
#             return redirect('university')
#
#         # Create new application
#         UserApplication.objects.create(
#             user=request.user,
#             college=college
#         )
#
#         messages.success(request, f'Successfully applied to {college.college_name}!')
#         return redirect('manage_applications')
#
#     except College.DoesNotExist:
#         messages.error(request, 'University not found.')
#         return redirect('university_recommendations')
#     except Exception as e:
#         messages.error(request, f'An error occurred: {str(e)}')
#         return redirect('university')
#
# @login_required
# def remove_application(request, application_id):
#     application = UserApplication.objects.get(
#         id=application_id,
#         user=request.user
#     )
#     application.delete()
#
#     return redirect('manage_applications')
#
# @login_required
# def book_seat(request, college_id):
#     """
#     View to handle booking a seat for a university
#     """
#     try:
#         # Find the college
#         college = College.objects.get(id=college_id)
#
#         # Check if application already exists
#         existing_application = UserApplication.objects.filter(
#             user=request.user,
#             college=college
#         ).first()
#
#         if existing_application:
#             messages.warning(request, f'You have already applied to {college.college_name}.')
#             return redirect('university')
#
#         # Create new application with additional details
#         UserApplication.objects.create(
#             user=request.user,
#             college=college,
#             status='APPLIED',
#             notes=json.dumps({
#                 'match_score': request.GET.get('match_score', ''),
#                 'graduation_rate': request.GET.get('graduation_rate', ''),
#                 'full_name': request.user.get_full_name(),
#                 'university_name': college.college_name
#             })
#         )
#
#         # Add success message
#         messages.success(request, f'Successfully booked a seat at {college.college_name}!')
#
#         # Redirect to manage applications
#         return redirect('manage_applications')
#
#     except College.DoesNotExist:
#         # Add error message if college not found
#         messages.error(request, 'University not found.')
#         return redirect('university_recommendations')
#     except Exception as e:
#         # Catch any other unexpected errors
#         messages.error(request, f'An error occurred: {str(e)}')
#         return redirect('university')


@login_required
def manage_applications(request):
    try:
        # Get all university applications for the user
        university_registrations = UniversityRegistration.objects.filter(user=request.user)

        # Prepare detailed information for each registration
        applications = []
        for registration in university_registrations:
            # Parse offered_courses JSON safely
            try:
                offered_courses = json.loads(registration.offered_courses) \
                    if registration.offered_courses else {}
            except json.JSONDecodeError:
                offered_courses = {}

            applications.append({
                'id': registration.id,
                'university_name': registration.university_name,
                'country': registration.country,
                'city': registration.city,
                'location': registration.location,
                'offered_courses': offered_courses
            })

        context = {
            'applications': applications,
            'has_registrations': bool(applications)
        }
    except Exception as e:
        # Log the error
        print(f"Error in manage_applications: {str(e)}")
        context = {
            'applications': [],
            'has_registrations': False,
            'error': 'An error occurred while fetching your applications.'
        }

    return render(request, 'manage_applications.html', context)


@login_required
def remove_application(request, application_id):
    try:
        # Find and delete the specific application
        application = UniversityRegistration.objects.get(
            id=application_id,
            user=request.user
        )
        application.delete()

        messages.success(request, f'Application for {application.university_name} has been removed.')
    except UniversityRegistration.DoesNotExist:
        messages.error(request, 'Application not found.')
    except Exception as e:
        print(f"Error removing application: {str(e)}")
        messages.error(request, 'An error occurred while removing the application.')

    return redirect('manage_applications')


@login_required
def add_application(request):
    if request.method == 'POST':
        try:
            # Get form data
            university_name = request.POST.get('university_name')
            country = request.POST.get('country')
            city = request.POST.get('city')

            # Check if university already exists for this user
            existing_application = UniversityRegistration.objects.filter(
                user=request.user,
                university_name=university_name
            ).exists()

            if existing_application:
                messages.warning(request, 'You have already applied to this university.')
                return redirect('manage_applications')

            # Create new application
            UniversityRegistration.objects.create(
                user=request.user,
                university_name=university_name,
                country=country,
                city=city,
                offered_courses=json.dumps({
                    'additional_info': 'No additional information'
                })
            )

            messages.success(request, f'Application for {university_name} added successfully.')
        except Exception as e:
            print(f"Error adding application: {str(e)}")
            messages.error(request, 'An error occurred while adding the application.')

        return redirect('manage_applications')

    # If not POST, render a form or redirect
    return redirect('manage_applications')


@login_required
def cancel_application(request):
    if request.method == 'POST':
        try:
            # Delete the user's university registration
            UniversityRegistration.objects.filter(user=request.user).delete()

            messages.success(request, 'Your university application has been cancelled successfully.')
            return redirect('manage_applications')

        except Exception as e:
            messages.error(request, 'An error occurred while cancelling your application.')
            print(f"Error in cancel_application: {str(e)}")
            return redirect('manage_applications')

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def book_university(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from request
            data = json.loads(request.body)
            university_name = data.get('university_name')

            # Check if user already has a university registration
            existing_registration = UniversityRegistration.objects.filter(user=request.user).first()

            if existing_registration:
                # If user already has a registration, update it
                existing_registration.university_name = university_name
                existing_registration.save()

                return JsonResponse({
                    'message': 'University registration updated successfully.',
                    'status': 'updated'
                })

            # Create new university registration
            UniversityRegistration.objects.create(
                user=request.user,
                university_name=university_name,
                # You might want to add more fields based on the data
                country=data.get('country', ''),
                state=data.get('state', ''),
                city=data.get('area', ''),
                location=f"Graduation Rate: {data.get('graduation_rate', '')}, "
                         f"Type: {data.get('organization_type', '')}, "
                         f"Financial Aid: {data.get('financial_aid', '')}",
                offered_courses=json.dumps({
                    'graduation_rate': data.get('graduation_rate', ''),
                    'organization_type': data.get('organization_type', ''),
                    'financial_aid': data.get('financial_aid', '')
                })
            )

            return JsonResponse({
                'message': 'University registered successfully.',
                'status': 'created'
            })

        except Exception as e:
            print(f"Error in book_university: {str(e)}")
            return JsonResponse({
                'error': 'Failed to register university. Please try again.',
                'details': str(e)
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def guidence(request):
    return render(request,'guidence.html')


from .models import UserAnalysisDB
from .forms import UserAnalysisForm


def user_analysis(request):
    if request.method == 'POST':
        form = UserAnalysisForm(request.POST)
        if form.is_valid():
            user_data = form.save(commit=False)

            # Perform classification
            classification = classify_student(user_data)
            user_data.classification = classification
            user_data.save()

            messages.success(request, f"Profile saved successfully! Classification: {classification}")
            return redirect('analysis_result', pk=user_data.pk)
    else:
        form = UserAnalysisForm()

    return render(request, 'user_analysis_form.html', {'form': form})


def analysis_result(request, pk):
    analysis = UserAnalysisDB.objects.get(pk=pk)
    return render(request, 'analysis_result.html', {'analysis': analysis})


def classify_student(user_data):
    # Calculate academics score deviation
    tenth_deviation = user_data.tenth_marks_total - user_data.tenth_marks_received
    twelfth_deviation = user_data.twelfth_marks_total - user_data.twelfth_marks_received

    sat_deviation = 0
    if user_data.sat_score_received and user_data.sat_score_total:
        sat_deviation = user_data.sat_score_total - user_data.sat_score_received

    # Total academic deviation
    total_deviation = tenth_deviation + twelfth_deviation + sat_deviation

    # Check for competition participation, extra-curricular activities, and skills
    has_competition = bool(user_data.competition_name)
    has_extra_curricular = bool(user_data.extra_curricular)
    has_skills = bool(user_data.skills)

    boolean_count = sum([has_competition, has_extra_curricular, has_skills])  # Count True values

    # Classification logic
    if total_deviation < 10 and user_data.avg_cgpa and user_data.avg_cgpa >= 8.5 and boolean_count >= 2:
        return "Top10"

    elif total_deviation < 20 and user_data.avg_cgpa and user_data.avg_cgpa >= 8.5 and boolean_count >= 1:
        return "Top50"

    elif total_deviation < 30 and (user_data.avg_cgpa is None or user_data.avg_cgpa >= 8.5):
        return "Top100"

    return "Regular"


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

