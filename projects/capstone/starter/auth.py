import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import os

AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN','lbluitt.us.auth0.com')
ALGORITHMS = os.environ.get('ALGORITHMS',['RS256'])
API_AUDIENCE = os.environ.get('API_AUDIENCE','https://casting-agency/')

# AuthError Exception
class AuthError(Exception):
    def __init__(self,error,status_code):
        self.error=error
        self.status_code=status_code

# Auth header
def get_token_auth_header():

    auth = request.headers.get('Authorization',None)

    if not auth:
        raise AuthError({
            'code':'authorization_header_missiong',
            'description':'Authorization header expected'
        },401)

    auth_header_parts = auth.split()

    if len(auth_header_parts)==1:
        raise AuthError({
            'code':'invalid_header',
            'description':'token not found'
        },401)

    if len(auth_header_parts)>2:
        raise AuthError({
            'code':'invalid_header',
            'description':'auth header must be a bearer token'
        },401)

    if auth_header_parts[0].lower()!='bearer':
        raise AuthError({
            'code':'invalid_header',
            'description':'auth header must start with "Bearer"'
        })

    token = auth_header_parts[1]
    return token

def check_permissions(permission,payload):

    if 'permissions' not in payload:
        raise AuthError({
            'code':'invalid_claims',
            'description':'permission not included in JWT'
        },400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code':'unauthorized',
            'description':'permission not found'
        },403)

    return True

def verify_decode_jwt(token):
    '''
    Verify and decode the given jwt token. if it's valid and can be properly decoded, return its payload
    '''
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)


    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            token=get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission,payload)
            return f(payload,*args,**kwargs)
        return wrapper
    return requires_auth_decorator