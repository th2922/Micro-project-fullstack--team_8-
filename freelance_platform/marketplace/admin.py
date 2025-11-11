from django.contrib import admin
from .models import UserProfile, Project, Bid

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'skills']
    list_filter = ['user_type']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'budget', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['project', 'freelancer', 'amount', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']