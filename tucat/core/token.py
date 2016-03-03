from __future__ import absolute_import

from allauth.socialaccount.models import SocialApp, SocialToken

def get_app_token(app_provider):
    app_token = {}

    social_app = SocialApp.objects.get(provider=app_provider)
    app_token = {'key': social_app.client_id, 'secret': social_app.secret}

    return app_token

def get_users_token(app_provider):
    user_tokens = []

    social_users = SocialToken.objects.filter(app__provider=app_provider)
    for one_user in social_users:
        user_tokens.append({'key' : one_user.token, 'secret' : one_user.token_secret})

    return user_tokens
