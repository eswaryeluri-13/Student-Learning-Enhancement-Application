# aitool/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import datetime
from django.http import JsonResponse
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import UserProfile
from PyPDF2 import PdfReader
from io import BytesIO

# Step 1: Collect user profiles and interests
user_profiles = UserProfile.objects.all()

# Step 2: Preprocess data
interests = [profile.interests for profile in user_profiles]

# Step 3: Convert interests to numerical vectors
vectorizer = TfidfVectorizer()
interests_matrix = vectorizer.fit_transform(interests)


User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Store the form data in the session
            request.session['username'] = form.cleaned_data['username']
            request.session['password'] = form.cleaned_data['password']
            request.session['name'] = form.cleaned_data['name']
            request.session['dob'] = form.cleaned_data['dob'].isoformat()
            request.session['education'] = form.cleaned_data['education']
            request.session['specialization'] = form.cleaned_data['specialization']
            request.session['university'] = form.cleaned_data['university']
            request.session['email'] = form.cleaned_data['email']
            request.session['skills'] = form.cleaned_data['skills']
            request.session['interests'] = form.cleaned_data['interests']

            # Save the form data to the database
            user_profile = form.save(commit=False)
            user_profile.skills = form.cleaned_data['skills']
            user_profile.interests = form.cleaned_data['interests']
            print(user_profile.skills)
            #user_profile.save()

            # Send OTP email
            email = form.cleaned_data['email']
            otp = get_random_string(length=6, allowed_chars='1234567890')
            subject = 'Your OTP for Registration'
            message = f"Hi {user_profile.username},\n\nThe OTP is to confirm your registration in our Aitool student portal.\n\nThe OTP: {otp}\n\nIf you want to register successfully, click the given OTP in the OTP verification site.\n\nFrom,\nAitool"
            from_email = 'eswaryelur13@gmail.com'
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)

            # Store OTP in session for verification
            request.session['otp'] = otp

            # Redirect to OTP verification page
            return redirect('aitool:otp_verification')

    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})



def login_user(request):
    login_unsuccessful = False
    username = None  # Initialize the variable

    if request.method == 'POST':
        form = LoginForm(request.POST)
        print(form.errors)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            print(username)

            try:
                user_profile = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                login_unsuccessful = True
            else:
                if password == user_profile.password:
                    login_unsuccessful = False
                    return redirect('aitool:reg_success', success_type='login', username=username)
                else:
                    login_unsuccessful = True

    else:
        form = LoginForm()

    # Check if the page is reloaded, set username to None and login_unsuccessful to False
    if request.method == 'GET' and request.session.get('login_reloaded'):
        request.session['login_reloaded'] = False  # Reset the session variable
        return render(request, 'login.html', {'form': form, 'login_unsuccessful': False, 'username': username})

    return render(request, 'login.html', {'form': form, 'login_unsuccessful': login_unsuccessful, 'username': username})



# In your view where you handle the login page load (GET request), set the session variable
def handle_login_page(request):
    request.session['login_reloaded'] = True
    return render(request, 'login.html', {'form': LoginForm()})




#@login_required(login_url='register')

def reg_success(request, success_type,username=None):
    success_messages = {
        'registration': 'Registration Successful!',
        'login': 'Login Successful!',
    }
    success_message = success_messages.get(success_type, 'Unknown Action')

    return render(request, 'success.html', {'success_message': success_type,'username':username})




def otp_verification(request):
    user_email = request.session.get('email', '')
    form = RegistrationForm()
    dob_str = request.session.get('dob')
    dob_date = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None   

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        # Retrieve OTP from session
        stored_otp = request.session.get('otp')
        print(entered_otp)
        print(stored_otp)

        if stored_otp and entered_otp == stored_otp:
            # OTP verification successful
            form_data = {
                'username': request.session.get('username'),
                'password': request.session.get('password'),
                'name': request.session.get('name'),
                'dob': dob_date,
                'education': request.session.get('education'),
                'specialization': request.session.get('specialization'),
                'university': request.session.get('university'),
                'email': user_email,
               'skills': request.session.get('skills').split(','),  # Ensure skills is a list
             'interests': request.session.get('interests').split(','),

            }

            form = RegistrationForm(form_data,files=request.FILES)
            print(form_data)
            print(form.is_valid())
            print(form.errors)

            if form.is_valid():
                # Save the form data to the database
                user_profile = form.save(commit=False)
                user_profile.skills = form.cleaned_data['skills']  # Set skills from form
                user_profile.interests = form.cleaned_data['interests'] 
                user_profile.save()
                # Redirect to a success page with registration type
                return redirect('aitool:reg_success', success_type='registration', username=user_profile.username)

        else:
            # Display an error message for invalid OTP
            error_message = 'Invalid OTP. Please enter the correct OTP.'
            return render(request, 'verify_otp.html', {'form': form, 'email': user_email, 'error_message': error_message})

    return render(request, 'verify_otp.html', {'form': form, 'email': user_email})

def char_with_gpt(prompt):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': 'Bearer OpenAI_API_key',  # Replace with your OpenAI_API_key with actual key
        'Content-Type': 'application/json'
    }

    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response_json = response.json()

    # Accessing the content of the generated message
    generated_content = response_json['choices'][0]['message']['content']
    return generated_content


def page(request):
    if request.method == 'POST':
        print(request.POST)
        user_input = request.POST['user_input']
        print(user_input)
        response = char_with_gpt(user_input)
        return render(request, 'landing.html', {'answer': response})

    return render(request, 'landing.html')
def courses(request):
    """
    View function to handle the course search request.
    """
    if request.method == 'POST':
        # Retrieve the course query from the form
        query = request.POST.get("course")+"courses"
        platforms=['udemy','coursera']
        generated_quries=[query+platform for platform in platforms]
        links=[]
        print(links)
        # Perform Google search
        for q in generated_quries:
            l = search_google(q)
            links.extend(l)
        
        return render(request,'courses.html',{'links':links})
    else:
        # Render the course search form
        return render(request, 'courses.html')
    

def search_google(query):
    api_key=open(r"C:\users\abhigna\Desktop\hackathon\demo\creds.txt",'r').readlines()[0] # API_KEY
    search_engine_id=open(r"C:\users\abhigna\Desktop\hackathon\demo\creds.txt",'r').readlines()[1]

    search_query=query
    url='https://www.googleapis.com/customsearch/v1'
    params={
    'q':search_query,
    'key':api_key,
    'cx':search_engine_id
    }

    response=requests.get(url,params=params)
    results=response.json()
    links=[]
    if 'items' in results:
        for item in results['items']:
            links.append(item['link'])
    return links
def get_similar_profiles(user_profile):
    user_interests = user_profile.interests
    user_vector = vectorizer.transform([user_interests])
    similarities = cosine_similarity(user_vector, interests_matrix)
    print(similarities)
    similar_profiles_indices=[]
    for idx in range(len(similarities[0])):
        print(similarities[0][idx],type(similarities[0][idx]))
        if similarities[0][idx]>0.0:
            similar_profiles_indices.append(idx+1)
    #similar_profiles_indices = similarities.argsort()[0][::-1]
    
    # Convert indices to integers
    #similar_profiles_indices = list(map(int, similar_profiles_indices))
    print(similar_profiles_indices)
    #similar_profiles_indices.remove(user_profile.id)
    # Retrieve similar profiles using integer indices
    similar_profiles = [user_profiles[idx-1] for idx in similar_profiles_indices]

    return similar_profiles

def home(request,username):
    user_profile = UserProfile.objects.get(username=username)
    recommendations = get_similar_profiles(user_profile)
    # Serialize recommendations to JSON
    recommendation_data = [{'email': profile.email, 'name': profile.name,'university': profile.university,'interests':profile.interests} for profile in recommendations]
    return render(request,'home.html',{'recommendation_data':recommendation_data})


def extract_text_from_pdf(pdf_data):
    text = ""
    pdf_reader = PdfReader(pdf_data)
    num_pages = len(pdf_reader.pages)
    for page_number in range(num_pages):
        text += pdf_reader.pages[page_number].extract_text()
    return text


def askques(request):
    if request.method=="POST":
        question=request.POST['ques']
        print(question)
        text_content = None
        print(request.FILES)
        uploaded_file = request.FILES.get('pdf_file')
        print(uploaded_file)
        if uploaded_file:
            pdf_data = BytesIO(uploaded_file.read())  # Read the uploaded file into a BytesIO object
            text_content = extract_text_from_pdf(pdf_data)
            #print(text_content)

        #print(text_content)
        c=text_content
        #print(c)
        #c=open("C:/Users/ABHIGNA/Desktop/hackathon/demo/ai.txt",'r').read()
        ans=ask(question,c)
        print(ans)
        return render(request,'askques.html',{'ans':ans,'q':question})
    return render(request,'askques.html')

def ask(q,c):
    from transformers import AutoModelForQuestionAnswering, AutoTokenizer,pipeline
    model_name='deepset/roberta-base-squad2'
    model=AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer=AutoTokenizer.from_pretrained(model_name)
    nlp=pipeline('question-answering',model=model,tokenizer=tokenizer)
    QA_input={'question':q,'context':c}
    res=nlp(QA_input)
    print(res)
    return res['answer']


















