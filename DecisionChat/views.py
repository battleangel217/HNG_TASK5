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
            # Extract the JSON-RPC request
            req_data = request.data
            rpc_id = req_data.get("id", str(uuid.uuid4()))
            message_parts = req_data.get("params", {}).get("message", {}).get("parts", [])
            user_question = None
            if message_parts:
                for part in message_parts:
                    if part.get("kind") == "text":
                        user_question = part.get("text")
                        break

            if not user_question:
                return JsonResponse({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": "No question provided"},
                    "id": rpc_id
                }, status=400)

            # Generate AI response using Gemini
            prompt = f"""
            You are a helpful decision assistant. The user says: "{user_question}".
            Respond with pros and cons for each choice and a final recommendation.
            Be concise and clear
            """

            model = genai.GenerativeModel("gemini-2.5-flash")
            ai_response = model.generate_content(prompt).text

            # Build A2A protocol response
            task_id = str(uuid.uuid4())
            context_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat() + "Z"

            response_data = {
                "jsonrpc": "2.0",
                "id": rpc_id,
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
                "id": req_data.get("id", 1)
            }, status=500)
