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

'''
def get_tokens(app_provider):
    tokens = []

    social_apps = SocialApp.objects.filter(provider=app_provider)

    for one_app in social_apps:
        #app_tokens.append({'key' : app.client_id, 'secret' : app.secret})
        app_token = {}
        users_tokens = {}

        social_users = SocialToken.objects.filter(app_id=one_app.id)

        app_token.append({'key' : one_app.client_id, 'secret' : one_app.secret})
        
        for one_user in social_users:
            users_tokens.append({'key' : one_user.token, 'secret' : one_user.token_secret})

        app_tokens.append({'app' : app_token, 'users' : users_tokens})

    return tokens
'''