from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Adds a section to show and modify 'role' field
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Roles and Permissions', {'fields': ('role',)}),
    )

    # Shows the role in the general user list
    list_display = ['username', 'email', 'role', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)