import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import re
from joblib import load

genai.configure(api_key="AIzaSyCPS2FFkq6iK1wlPzqn_614B1xLanC3pCc")
# Model Initialization
model = genai.GenerativeModel('gemini-pro')

# Create your views here.

def chatbot(request):
    return render(request, 'chatbot.html')


greeting_responses = {
    "hello": "Hello!",
    "hi": "Hi there!",
    "hey": "Hey!",
    "good morning": "Good morning!",
    "good afternoon": "Good afternoon!",
    "good evening": "Good evening!",
    "how are you": "Hi, how are you?",
    "what's up": "What's up?",
    "howdy": "Howdy!",
    "greetings": "Greetings!",
    "salutations": "Salutations!",
    "yo": "Yo!",
    "nice to meet you": "Hi, it's nice to meet you!",
    "your day": "Hello, how's your day going?",
    "what's new": "Hey, what's new?",
    "long time": "Hey, long time no see!",
    "what's happening": "Hey, what's happening?",
    "how have you been": "Hi, how have you been?",
    "what's cooking": "Hey, what's cooking?",
    "how's everything": "Hey, how's everything?",
    "your day been": "Hi, how's your day been?",
    "what's crackin'": "Hey, what's crackin'?",
    "good to see you": "Hi, good to see you!"
}
pkeys = ['profit', 'sales']
lkeys = ['predict', 'expecting', 'price', 'salary']


def predfined_response(message):
    qs = message.split()
    print(qs)
    for i in qs:
        if i in pkeys:
            return "Our company profit is about ₹ 545000 per month"
        elif i in lkeys:
            return "Do you want to predict the salary fee ? Give y or n "
    return None

#
# def extract_course_and_year(message):
#     # Define regular expressions to match courses and years
#     course_pattern = r'(python|datascience|java)'
#     year_pattern = r'\b\d{4}\b'  # Assuming the year is a 4-digit number
#
#     # Extract course and year using regular expressions
#     course_match = re.search(course_pattern, message, re.IGNORECASE)
#     year_match = re.search(year_pattern, message)
#
#     # Initialize variables for course and year
#     course = None
#     year = None
#
#     # Store the course and year if found
#     if course_match:
#         course = course_match.group(0)
#     if year_match:
#         year = year_match.group(0)
#
#     if course != None and year != None:
#         return f"course = {course} , year = {year}"
#     else:
#         return None


@csrf_exempt
def chatbot_response(request):
    if request.method == 'POST':
        # Parse the incoming JSON data
        received_data = json.loads(request.body.decode('utf-8'))
        um = received_data.get('message', '')
        user_message = um.lower()

        # Process user message and generate bot response
        if user_message.lower() == 'y':
            bot_response = "Click the above predict button"

        elif user_message.lower() in greeting_responses.keys():
            bot_response = f"{greeting_responses[user_message]}"

        elif predfined_response(user_message) != None:
            bot_response = predfined_response(user_message)
        else:
            bot_response = generate_gemini_response(user_message)

        # Return the bot response in JSON format
        return JsonResponse({'message': bot_response})

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_gemini_response(message):
    # Generate response using Gemini model
    response = ""
    for chunk in model.generate_content(message, stream=True):
        response += chunk.text.strip('*')  # Remove stars

    # Extract only important data
    important_data = ""
    lines = response.split('\n')
    for line in lines:
        if line.strip().startswith(('*', '#', '-', '`', '**', '-')):  # Skip lines starting with certain characters
            continue
        else:
            important_data += line + '\n'

    return important_data.strip()


import json
import pickle
import numpy as np

locations = None
job_roles = None
comp_size = None
emp_type = None
experiences = None
chat_model = None

import os


def load_saved_artifacts():
    print("Loading saved artifacts...start")

    global locations
    global job_roles
    global comp_size
    global emp_type
    global experiences
    global chat_model

    with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts"
              r"\New_data\comp_locations_columns.json",
              'r') as f:
        dl = json.load(f)['comp_location_columns']
        locations = dl
    global model

    with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts"
              r"\New_data\job_columns.json", 'r') as f:
        dm = json.load(f)['job_columns']
        job_roles = dm

    with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts\New_data\comp_size_columns.json",
              'r') as f:
        dm = json.load(f)['comp_size_columns']
        comp_size = dm

    with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts\New_data\emp_type_columns.json",
              'r') as f:
        dm = json.load(f)['emp_type']
        emp_type = dm

    with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts"
              r"\New_data\exp_columns.json", 'r') as f:
        dm = json.load(f)['exp_columns']
        experiences = dm

    # with open(r"C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts\New_data\newmodel.joblib",
    #           'rb') as f:
    #     chat_model = pickle.load(f)

    print("loading artifacts ....done")


def prediction_Page(request):
    sy, sexp, stype, js, slocation, ssize = '', '', '', '', '', ''
    l = load_saved_artifacts()
    jobs = job_roles
    location = locations
    exp = experiences
    type = emp_type
    size = comp_size
    global chat_model
    chat_model = load(r'C:\Users\kuttu\PycharmProjects\Gemini_Chatbot_folder\gemini_chatbot_project\chatapp\artifacts'
                      r'\New_data\newmodel.joblib')
    if request.method == "POST":
        yr = request.POST['year']
        selexp = request.POST['exp']
        seltype = request.POST['type']
        jobselec = request.POST['job']
        comp_loc = request.POST['loc']
        siz = request.POST['size']
        sy = yr
        sexp = selexp
        stype = seltype
        js = jobselec
        slocation = comp_loc
        ssize = siz
        print('Selected values are == ', int(yr), experiences[sexp],emp_type[stype],job_roles[js],locations[slocation],comp_size[ssize])
        result = predict_price(int(yr), experiences[sexp],emp_type[stype],job_roles[js],locations[slocation],comp_size[ssize])
        return render(request, 'prediction.html',
                      {'sy': sy, 'sjob': js, 'stype': stype, 'sexp': sexp, 'sloc': slocation, 'jr': jobs,
                       'ssize': ssize,
                       'loc': location, 'exp': exp, 'type': type, 'size': size,'result':result})

    return render(request, 'prediction.html',
                  {'sy': sy, 'sjob': js, 'stype': stype, 'sexp': sexp, 'sloc': slocation, 'jr': jobs, 'loc': location,
                   'exp': exp, 'type': type, 'size': size})


def predict_price(yr, exp, etype, job, comp, size):
    result = chat_model.predict([[yr, exp, etype, job, comp, size]])

    return result[0]