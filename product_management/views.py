# from  Django
from django.shortcuts import render

# from rest_framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# from utils
from invertory_management.utils import handle_exceptions

# from serializers
from .serializers import ProductSerializer

# from models
from .models import Product

# from jwt authorization
from invertory_management.jwt_authorization import JWTAuthorization


# Create your views here.
class ProductAPIView(APIView):
    permission_classes = [JWTAuthorization]
    serializer_class = ProductSerializer

    @handle_exceptions(is_status=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Product created successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProductListAPIView(APIView):
    permission_classes = [JWTAuthorization]
    serializer_class = ProductSerializer

    @handle_exceptions(is_status=True)
    def get(self, request):
        user = request.user
        # Check if user is admin or superuser
        if user.is_staff or user.is_superuser:
            products = Product.objects.all().order_by('-created_at')
            serializer = self.serializer_class(products, many=True)
            return Response({
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK)
        
        if not user.is_admin_approve:
            return Response(
                {
                    "status": "error",
                    "message": "User is not approved by admin."
                },  status=status.HTTP_403_FORBIDDEN)

        products = Product.objects.filter(created_by=user, deleted_at = False).order_by('-created_at')
        if not products:
            return Response(
                {
                    "status": "error",
                    "message": "No products found for this user.",
                    "data": []
                },
                status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(products, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class ProductUpdateAPIView(APIView):
    permission_classes = [JWTAuthorization]
    serializer_class = ProductSerializer

    @handle_exceptions(is_status=True)
    def put(self, request, pk):
        # only admin, superuser or creator can update product
        product = Product.objects.filter(pk=pk, deleted_at=False).first()
        if not product:
            return Response(
                {
                    "status": "error",
                    "message": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(product, data=request.data, partial=True, context={'request': request})

        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Product updated successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "errors": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST)

    @handle_exceptions(is_status=True)
    def delete(self, request, pk):
        user = request.user

        # Try to get the product
        product = Product.objects.filter(id=pk, deleted_at=False).first()
        if not product:
            return Response(
                {
                    "status": "error",
                    "message": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND)

        if not ((product.created_by == user and user.admin_approved) or user.is_superuser or user.admin):
            return Response(
                {
                    "status": "error",
                    "message": "You do not have permission to delete this product."
                },
                status=status.HTTP_403_FORBIDDEN)

        product.deleted_at = True  # Mark as delete
        product.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
