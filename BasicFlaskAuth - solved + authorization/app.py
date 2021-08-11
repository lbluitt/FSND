from flask import Flask, request, abort
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen


app = Flask(__name__)

AUTH0_DOMAIN = "lbluitt.us.auth0.com"
ALGORITHMS = ['RS256']
API_AUDIENCE = "lbluitt"


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token


def verify_decode_jwt(token):
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

def check_permissions(permission,payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)    
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True



def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission,payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator

@app.route('/headers')
@requires_auth('get:images')
def headers(payload):
    print(payload)
    return 'Access Granted'

@app.route('/images')
@requires_auth('get:images')
def images(payload):
    print(payload)
    return 'Access Granted'

# Postman test
# pm.test("Status code is 401",function(){
#     pm.response.to.have.status(401);
# });

# bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJMejZSMElWUnRpRDh4cXNEalY1NSJ9.eyJpc3MiOiJodHRwczovL2xibHVpdHQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwZjZhNzViNjEwYTc2MDA2OWVjOWQ0ZCIsImF1ZCI6ImxibHVpdHQiLCJpYXQiOjE2MjgxMzU5MDksImV4cCI6MTYyODE0MzEwOSwiYXpwIjoiNXhKTkdCVkVNazk4VzZLOGpPeW5OZGFpTUlMRjFRamsiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDppbWFnZXMiLCJwb3N0OmltYWdlcyJdfQ.Pzey_XhSokQ-eCOZRedH7-hbkadBvOJsFmbwSr1sO-17DlmvxUj5FmIqNi5HCHjxtFqjv6cHtK1huKOQj76c8j7XAKwjaozxTlHBohe3key1sxu5kUfppA-xB15VpBt8vDICAUfshlB168iBribDxY4jh-4_FK9AhdDfSXeI9ufla5FFO85KxFgfZjsYhsQcA3yGJxLKchjUvQtvNLHglOeV3L-KWJVL43vU_DDQsOteE9BAfkAVeioMidWOvxDfhLFQYs0ZQFpBPYurrncgHmBx9sdOISMXmMNG4ar2rgfIjp-l22OVdY2M1ThEUxmAlqLFp2v4XDNzunMp551EzQ
#     eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InJMejZSMElWUnRpRDh4cXNEalY1NSJ9.eyJpc3MiOiJodHRwczovL2xibHVpdHQudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDYwZjZhNzViNjEwYTc2MDA2OWVjOWQ0ZCIsImF1ZCI6ImxibHVpdHQiLCJpYXQiOjE2MjgxMzc2ODgsImV4cCI6MTYyODE0NDg4OCwiYXpwIjoiNXhKTkdCVkVNazk4VzZLOGpPeW5OZGFpTUlMRjFRamsiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbXX0.NmlOQeoQU59dE4Y3oVZkdsaZ6gz8shUcvuo1XIYMe5ZAPEmAb3MQ8favkmyF86rWu19ivw3_HI7dLjla-y4TJKHiZUphh9jGMHC1_Y61t--Ob86aqSIEQP1HjhH5qcBMvPfVc5N_ICT0tGNAx6PM02aDDIvTfkt9rvpys2q_q-lu-2HvcP5L4xYoFgoUUPE8yoGxjYc5d1CHM8N-fBK2r5HWKfs3dlQqm26TrXEJiyEl-WpdjXU6VEguzTRoCuH_--OZFCp24L4NQDoK8gB7jl8MV6A7udmHhAB6EbEq4bRitP9VPDTgnxP4OzkCKlXJWsNFqW6ASQoVxkSgwv68dQ