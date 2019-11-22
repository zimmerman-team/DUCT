import json
import logging
import os
from functools import wraps

import jwt
import rest_framework
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from django.http import HttpResponseForbidden, JsonResponse
from graphene_django.views import GraphQLView, HttpError
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.permissions import AllowAny
from six.moves.urllib import request as req
from django.conf import settings

import gql.utils
from gql.utils import set_session_email


def get_token_auth_header(cls):
    """
    Obtains the access token from the Authorization Header
    """
    auth = cls.request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope():
    """
    Determines if the required scope is present in the access token
    """
    def require_scope(f):
        if settings.UNIT_TEST:
            return f

        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                token = get_token_auth_header(args[0])
                AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
                API_IDENTIFIER = os.environ.get('API_IDENTIFIER')
                jsonurl = req.urlopen(
                    'https://' + AUTH0_DOMAIN + '/.well-known/jwks.json'
                )
                jwks = json.loads(jsonurl.read())
                cert = '-----BEGIN CERTIFICATE-----\n' + \
                        jwks['keys'][0]['x5c'][0] + \
                        '\n-----END CERTIFICATE-----'
                certificate = load_pem_x509_certificate(
                    cert.encode('utf-8'), default_backend()
                )
                public_key = certificate.public_key()
                decoded = jwt.decode(
                    token,
                    public_key,
                    audience=API_IDENTIFIER, algorithms=['RS256']
                )

                if decoded.get("email_verified"):
                    # Save user email for the auto messaging
                    # And set session as global variable
                    # function set_user_email will return session key
                    gql.utils.email_session_key = set_session_email(
                        decoded.get('email')
                    )

                    return f(*args, **kwargs)

            except Exception as e:
                logging.exception(e)

            response = JsonResponse(
                {'message': 'You don\'t have access to this resource'}
            )
            response.status_code = 403
            return response

        return decorated
    return require_scope


class AuthenticatedGraphQLView(GraphQLView):

    @requires_scope()
    def parse_body(self, request):
        if isinstance(request, rest_framework.request.Request):
            return request.data
        return super(AuthenticatedGraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(AuthenticatedGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((AllowAny, ))(view)
        view = authentication_classes((TokenAuthentication, ))(view)
        view = api_view(['POST'])(view)
        return view

    def execute_graphql_request(
        self, request, data, query, variables, operation_name,
        show_graphiql=False
    ):
        if isinstance(data, JsonResponse):
            if data.status_code == 403:
                raise HttpError(
                    HttpResponseForbidden(data.content)
                )

        return super(AuthenticatedGraphQLView, self).execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql
        )
