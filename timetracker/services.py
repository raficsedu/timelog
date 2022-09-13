from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from .middleware import get_request
from .settings import SIMPLE_JWT


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'validity': SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] / 60
    }


def get_current_user(request):
    user = request.GET.get('user')
    if user:
        return user
    token = request.headers['Authorization'].split(' ')[1]
    try:
        return AccessToken(token)['user_id']
    except TokenError as e:
        raise InvalidToken(e.args[0])


def get_user_from_token(token):
    return AccessToken(token)['user_id']


def get_api_token():
    return get_request().headers['Authorization'].split(' ')[1]


def format_response(data=[], message=None, status=200, count=0, metadata=[]):
    api_output = {'status': status, 'message': message}

    if count:
        api_output['count'] = count

    api_output['results'] = data

    if metadata:
        api_output['metadata'] = metadata

    return api_output
