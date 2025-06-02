# from  Django
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import login, logout

# from rest_framework
from  rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# from models
from user_management.models import User, Token

# from jwt authorization
from invertory_management.jwt_authorization import JWTAuthorization

# from utils
from invertory_management.utils import handle_exceptions, get_tokens_for_user
from invertory_management.renderers import UserRenderer

# from serializers
from user_management.serializers import LoginUserSerializer, RegisterUserSerializer, UserSerializer, TokenSerializer


# Create your views here.

class UserRegisterView(APIView):
    
    renderer_classes = [UserRenderer]
    serializer_class = RegisterUserSerializer

    @handle_exceptions(is_status=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Gererate token for the user
            token =  get_tokens_for_user(user)
            token, is_created = Token.objects.get_or_create(
                access_token=token.get("access"), 
                refresh_token=token.get("refresh"), 
                user=user
            )

            return Response({
                "status": "success",
                "message": "User registered successfully. Please wait for admin approval.",
                "data": serializer.data,
                "tokens": TokenSerializer(token).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    serializer_class = LoginUserSerializer
    # permission_classes = [JWTAuthorization]

    @handle_exceptions(is_status=True)
    def post(self, request):

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']  
            if user.is_admin_approve:
                login(request, user=user)
                # Generate token for the user
                token = get_tokens_for_user(user)
                token, is_created = Token.objects.get_or_create(access_token=token.get("access"), refresh_token=token.get("refresh"), user=user)

                return Response({
                    "status": "success",
                    "message": "Login successful.",
                    "data": serializer.data,
                    "tokens": TokenSerializer(token).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "User account is not approved by admin. Please wait for admin approval."
                }, status=status.HTTP_403_FORBIDDEN)
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Get all users aand admin approved users
class UserListAPIView(APIView):
    permission_classes = [JWTAuthorization]
    renderer_classes = [UserRenderer]
    serializer_class = UserSerializer

    @handle_exceptions(is_status=True)
    def get(self, request):
        user = request.user
        print(f"User: {user.username}, is_superuser: {user.is_superuser}, is_staff: {user.is_staff}")
        if user.is_superuser or user.is_staff:
            users =  User.objects.filter(is_superuser=False, is_staff=False)
            serializer = self.serializer_class(users, many=True)
            return Response({
                "status": "success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "error",
            "message": "You do not have permission to view all users."
        }, status=status.HTTP_403_FORBIDDEN)
    

class GetAllApprovedUsersAPIView(APIView):
    permission_classes = [JWTAuthorization]
    renderer_classes = [UserRenderer]
    serializer_class = UserSerializer

    @handle_exceptions(is_status=True)
    def get(self, request):
        user = request.user
        if not user.is_superuser or not user.is_staff:
            return Response({
                "status": "error",
                "message": "You do not have permission to view approved users."
            }, status=status.HTTP_403_FORBIDDEN)
        # Get all users who are admin approved
        # and not superuser or admin
        # This is to ensure that only active users are returned
        approved_users = User.objects.filter(is_active=True, is_admin_approve=True, is_superuser=False, is_staff=False)
        serializer = self.serializer_class(approved_users, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class GetUnApprovedUsersAPIView(APIView):
    permission_classes = [JWTAuthorization]
    renderer_classes = [UserRenderer]
    serializer_class = UserSerializer

    @handle_exceptions(is_status=True)
    def get(self, request):
        user = request.user
        if not user.is_superuser or not user.is_staff:
            return Response({
                "status": "error",
                "message": "You do not have permission to view unapproved users."
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get all users who are not admin approved
        unapproved_users = User.objects.filter(is_active=True, is_admin_approve=False, is_superuser=False, is_staff=False)
        serializer = self.serializer_class(unapproved_users, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class AdminApproveUserAPIView(APIView):

    permission_classes = [JWTAuthorization]
    renderer_classes = [UserRenderer]
    serializer_class = UserSerializer

    @handle_exceptions(is_status=True)
    def post(self, request, pk):
        user = request.user
        if not user.is_superuser and not user.is_staff:
            return Response({
                "status": "error",
                "message": "You do not have permission to approve users."
            }, status=status.HTTP_403_FORBIDDEN)
         
        user_to_approve = User.objects.filter(id=pk, is_superuser=False, is_staff=False).first()
        if not user_to_approve:
            return Response({
                "status": "error",
                "message": "User not found or user is admin user."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user_to_approve.is_admin_approve:
            user_to_approve.is_admin_approve = False
            user_to_approve.save()
            return Response({
                "status": "success",
                "message": "User is already approved. User is now deactivated.",
                "data": {
                    "user_id": user_to_approve.id,
                    "username": user_to_approve.username,
                    "email": user_to_approve.email,
                    "is_admin_approved": user_to_approve.is_admin_approve
                }
            }, status=status.HTTP_200_OK)
      
        user_to_approve.is_admin_approve = True
        user_to_approve.save()
        return Response({
            "status": "success",
            "message": "User approved successfully.",
            "data": {
                "user_id": user_to_approve.id,
                "username": user_to_approve.username,
                "email": user_to_approve.email,
                "is_admin_approved": user_to_approve.is_admin_approve
            }
        }, status=status.HTTP_200_OK)
        

class LogoutView(APIView):
    """ User logout view """

    renderer_classes = [UserRenderer]
    permission_classes = [JWTAuthorization]

    @handle_exceptions()
    def get(self, request):

        token = request.headers.get("Authorization").split(" ")[1]
        Token.objects.filter(Q(access_token=token) | Q(refresh_token=token) | Q(user=request.user.id)).delete()
        logout(request)
        return Response({"message": "Logout Successful..!", "status":"success"}, status=status.HTTP_200_OK)