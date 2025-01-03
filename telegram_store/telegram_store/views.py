from django.views.generic import TemplateView


class HomePage(TemplateView):
    template_name = "home.html"

# with below code you can start or stop bot remotely
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import subprocess

# @csrf_exempt
# def control_bot(request):
#     bot_script_path = "<absolute-path-to-bot>"
#     python_path = "<absolute-path-to-venv>"
# 
#     if request.method == "GET":
#         action = request.GET.get("action")
#         if action == "start":
#             # Check if bot is already running
#             result = subprocess.run(
#                 ["pgrep", "-f", bot_script_path],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#             if result.stdout:
#                 return JsonResponse({"message": "Bot is already running."}, status=200)
#             else:
#                 subprocess.Popen([python_path, bot_script_path])
#                 return JsonResponse({"message": "Bot started successfully."}, status=200)
#         elif action == "stop":
#             subprocess.run(["pkill", "-f", bot_script_path])
#             return JsonResponse({"message": "Bot stopped successfully."}, status=200)
#         else:
#             return JsonResponse({"error": "Invalid action."}, status=400)
#     return JsonResponse({"error": "Invalid request method."}, status=405)
