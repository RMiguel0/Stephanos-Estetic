# SE_users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        host = request.get_host()  # 'localhost:8000' o '127.0.0.1:8000'
        origin_map = {
            "localhost:8000":   "http://localhost:5173",
            "127.0.0.1:8000":   "http://127.0.0.1:5173",
        }
        origin = origin_map.get(host, "http://localhost:5173")
        return f"{origin}/profile"
