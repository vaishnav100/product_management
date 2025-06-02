from django.contrib import admin
from .models import User, Token

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id' ,'username', 'email', 'is_admin_approve', 'is_staff', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    list_filter = ('is_admin_approve', 'is_staff')
    ordering = ('-created_at',)

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'access_token', 'refresh_token', 'created_at', 'updated_at')
    search_fields = ('user__username', 'access_token', 'refresh_token')
    list_filter = ('created_at',)
    ordering = ('-created_at',)