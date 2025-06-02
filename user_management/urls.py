from django.urls import path, include
from user_management.views import UserRegisterView, UserLoginView, GetAllApprovedUsersAPIView, GetUnApprovedUsersAPIView, UserListAPIView, AdminApproveUserAPIView, LogoutView
urlpatterns = [
  path('register/', UserRegisterView.as_view(), name='user_register'),
  path('login/', UserLoginView.as_view(), name='user_login'),
  path("logout/", LogoutView.as_view(), name="user_logout"),
  #admin API's
  path("all_users/", UserListAPIView.as_view(), name="all_users"),
  path("approved_users/", GetAllApprovedUsersAPIView.as_view(), name="approved_users"),
  path("unapproved_users/", GetUnApprovedUsersAPIView.as_view(), name="unapproved_users"),
  path("approve_user/<int:pk>/", AdminApproveUserAPIView.as_view(), name="approve_user"),

]
