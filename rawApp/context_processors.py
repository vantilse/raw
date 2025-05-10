from .models import Profile

def profile(request):
    try:
        return {'user_profile': request.user.profile}
    except:
        return {}