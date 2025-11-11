#!/usr/bin/env python
"""
Test script to debug email configuration and freelancer emails.
Run: python manage.py shell < test_email.py
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'freelance_platform.settings')
django.setup()

from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from marketplace.models import Bid, UserProfile

# Check email backend configuration
print("=" * 60)
print("EMAIL CONFIGURATION")
print("=" * 60)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print()

# Check all users and their emails
print("=" * 60)
print("USERS AND THEIR EMAILS")
print("=" * 60)
users = User.objects.all()
for user in users:
    try:
        profile = UserProfile.objects.get(user=user)
        user_type = dict(UserProfile.USER_TYPES).get(profile.user_type, profile.user_type)
    except UserProfile.DoesNotExist:
        user_type = "No profile"
    print(f"Username: {user.username} | Email: {user.email} | Type: {user_type}")
print()

# Check freelancers specifically
print("=" * 60)
print("FREELANCERS")
print("=" * 60)
freelancers = UserProfile.objects.filter(user_type='freelancer')
for profile in freelancers:
    print(f"Freelancer: {profile.user.username} | Email: {profile.user.email}")
print()

# Check recent bids
print("=" * 60)
print("RECENT BIDS")
print("=" * 60)
recent_bids = Bid.objects.select_related('freelancer', 'project').order_by('-created_at')[:5]
for bid in recent_bids:
    print(f"Freelancer: {bid.freelancer.username} | Project: {bid.project.title} | Email: {bid.freelancer.email} | Accepted: {bid.is_accepted}")
print()

# Test email sending
print("=" * 60)
print("TEST EMAIL SEND")
print("=" * 60)
try:
    # Send a test email to the first user with an email
    test_user = User.objects.filter(email__isnull=False).exclude(email='').first()
    if test_user:
        print(f"Sending test email to: {test_user.email}")
        result = send_mail(
            subject='Test Email from FreelanceHub',
            message='This is a test email to verify your email configuration is working.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_user.email],
            fail_silently=False
        )
        print(f"Email send result: {result}")
    else:
        print("No users with email addresses found!")
except Exception as e:
    print(f"ERROR sending test email: {e}")
    import traceback
    traceback.print_exc()
