import uuid
from django.http import JsonResponse
from rest_framework.views import APIView
from django.conf import settings
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key=settings.GEMINI_API_KEY)

class ChatView(APIView):
    def post(self, request):
        try:
            user_input = request.data.get("question", "").strip()
            if not user_input:
                return JsonResponse({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": "Question is required."},
                    "id": 1
                }, status=400)

            # Generate AI response
            prompt = f"""
            You are a helpful decision assistant. The user says: "{user_input}".
            Respond with pros and cons for each choice and a final recommendation.
            Be concise and clear.
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            ai_response = model.generate_content(prompt).text

            # Create task/context IDs
            task_id = str(uuid.uuid4())
            context_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Build JSON-RPC A2A response
            response_data = {
                "jsonrpc": "2.0",
                "id": task_id,
                "result": {
                    "id": task_id,
                    "contextId": context_id,
                    "status": {
                        "state": "completed",
                        "timestamp": timestamp,
                        "message": {
                            "kind": "message",
                            "role": "agent",
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": ai_response
                                }
                            ],
                            "messageId": str(uuid.uuid4()),
                            "taskId": task_id
                        }
                    },
                    "artifacts": [
                        {
                            "artifactId": str(uuid.uuid4()),
                            "name": "Decision Assistant Response",
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": ai_response
                                }
                            ]
                        }
                    ],
                    "kind": "task"
                }
            }

            return JsonResponse(response_data, safe=False, status=200)

        except Exception as e:
            return JsonResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32000, "message": str(e)},
                "id": 1
            }, status=500)
