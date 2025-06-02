

# From rest_framework 
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
import jwt
from django.conf import settings
from user_management.models import User, Token
from django.db.models import Q


class JWTAuthorization(permissions.BasePermission):

    @staticmethod
    def decode_jwt_token(token):
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return decoded_token
        except:
            return None
    
    
    def authenticate(self, request):
        try:
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return None

            token = auth_header.split(' ')[-1]

            if Token.objects.filter(Q(access_token=token) | Q(refresh_token=token)).exists():
                            
                decoded_token = self.decode_jwt_token(token)

                if decoded_token:
                    user_id = decoded_token['user_id']
                    try:
                        user = User.objects.filter(id=user_id).first()

                        return user
                    except User.DoesNotExist:
                        return None
                return None
            else :
                return None
        except Exception as e:
            raise AuthenticationFailed(f"Token verification failed: {str(e)}")
        

    def has_permission(self, request, view):
        user = self.authenticate(request)
        request.user = user  # Set the authenticated user in the request
        
        return user is not None