from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Post
from . import forms 
import google.generativeai as genai
import json
import logging


API_KEY = "AIzaSyCxUMAoBFLJtVVtEWcn5CDXWhbJ7jVtNWk"

logging.basicConfig(filename='gemini_ai.log', level=logging.ERROR)

@login_required(login_url="/users/login/")
def post_new(request):
    if request.method == 'POST': 
        form = forms.CreatePost(request.POST, request.FILES) 
        if form.is_valid():
            newpost = form.save(commit=False)
            if request.user.is_authenticated:
                newpost.author = request.user 

                newpost.bot_response = call_gemini_ai(newpost.Message)
                newpost.bot_timestamp = timezone.now() 
                newpost.save()

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'author': newpost.author.username,
                        'content': newpost.Message,
                        'timestamp': newpost.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'bot_response': newpost.bot_response,
                        'bot_timestamp': newpost.bot_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    })
                return redirect('posts:list')
        else:
            return JsonResponse({'error': form.errors}, status=400)
    else:
        form = forms.CreatePost()
    return render(request, 'posts/post_new.html', {'form': form})

def call_gemini_ai(prompt):
    """
    Function to send a prompt to Gemini AI using the google.generativeai library and get a response.
    """
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            max_output_tokens=100,
            temperature=2.0,                              
            )
        )
        return response.text  
    except Exception as e:
        logging.error(f"Error communicating with Gemini AI: {str(e)}")
        return f"An error occurred while processing your request."


@csrf_exempt
def chatbot_response(request):
    """
    Endpoint to handle chatbot interactions.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            user_message = body.get("message", "")
            if user_message:
                bot_response = call_gemini_ai(user_message)
                return JsonResponse({"response": bot_response})
            return JsonResponse({"error": "No message provided."}, status=400)
        except json.JSONDecodeError:
            logging.error("Invalid JSON format.")
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method. Please use POST."}, status=405)

    
