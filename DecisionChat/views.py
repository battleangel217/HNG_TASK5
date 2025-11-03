from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)

# Create your views here.

class ChatView(APIView):
    def post(self, request):
        data = request.data.get("question", "Help me decide something")

        prompt = f"""
            You are a helpful decision assistant that gives pros and cons of user choices.
            The user says: "{data}"
            Respond clearly with:
            1. A list of pros and cons
            2. A final recommendation with reasoning (You must give a final decision. MUST)
            """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        return Response({"response": response.text}, status=status.HTTP_200_OK)




