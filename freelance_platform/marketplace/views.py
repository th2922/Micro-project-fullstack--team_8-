from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging
from .models import Project, Bid, UserProfile
from .forms import UserRegisterForm, UserProfileForm, ProjectForm, BidForm

logger = logging.getLogger(__name__)

def home(request):
    projects = Project.objects.filter(status='open')[:6]
    return render(request, 'marketplace/home.html', {'projects': projects})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data.get('user_type')
            )
            messages.success(request, 'Account created successfully!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'marketplace/register.html', {'form': form})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'marketplace/profile.html', {'form': form, 'profile': profile})

@login_required
def project_list(request):
    projects = Project.objects.filter(status='open')
    return render(request, 'marketplace/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    bids = Bid.objects.filter(project=project)
    user_has_bid = bids.filter(freelancer=request.user).exists()
    return render(request, 'marketplace/project_detail.html', {
        'project': project,
        'bids': bids,
        'user_has_bid': user_has_bid
    })

@login_required
def create_project(request):
    try:
        if request.user.userprofile.user_type != 'client':
            messages.error(request, 'Only clients can post projects!')
            return redirect('home')
    except:
        messages.error(request, 'Please complete your profile first!')
        return redirect('profile')
    
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.client = request.user
            project.save()
            messages.success(request, 'Project posted successfully!')
            return redirect('my_projects')
    else:
        form = ProjectForm()
    return render(request, 'marketplace/create_project.html', {'form': form})

@login_required
def my_projects(request):
    if hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'client':
        projects = Project.objects.filter(client=request.user)
    else:
        projects = Project.objects.filter(assigned_to=request.user)
    return render(request, 'marketplace/my_projects.html', {'projects': projects})

@login_required
def place_bid(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    try:
        if request.user.userprofile.user_type != 'freelancer':
            messages.error(request, 'Only freelancers can place bids!')
            return redirect('project_detail', pk=pk)
    except:
        messages.error(request, 'Please complete your profile first!')
        return redirect('profile')
    
    if Bid.objects.filter(project=project, freelancer=request.user).exists():
        messages.error(request, 'You have already bid on this project!')
        return redirect('project_detail', pk=pk)
    
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.project = project
            bid.freelancer = request.user
            bid.save()
            messages.success(request, 'Bid placed successfully!')
            return redirect('project_detail', pk=pk)
    else:
        form = BidForm()
    return render(request, 'marketplace/place_bid.html', {'form': form, 'project': project})

@login_required
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    
    if bid.project.client != request.user:
        messages.error(request, 'You are not authorized!')
        return redirect('home')
    
    bid.is_accepted = True
    bid.save()
    
    bid.project.assigned_to = bid.freelancer
    bid.project.status = 'in_progress'
    bid.project.save()
    # send notification email to freelancer
    try:
        subject = f"Your bid for '{bid.project.title}' was accepted"
        context = {
            'freelancer': bid.freelancer,
            'project': bid.project,
            'bid': bid,
            'site_name': 'FreelanceHub'
        }
        text_body = render_to_string('marketplace/emails/accepted_bid_email.txt', context)
        html_body = render_to_string('marketplace/emails/accepted_bid_email.html', context)

        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@freelancehub.local')
        to_email = [bid.freelancer.email]

        logger.info(f"Attempting to send email to {to_email} with subject: {subject}")
        
        email_message = EmailMultiAlternatives(subject, text_body, from_email, to_email)
        email_message.attach_alternative(html_body, "text/html")
        email_message.send(fail_silently=False)
        
        logger.info(f"Email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}", exc_info=True)

    messages.success(request, 'Bid accepted successfully! The freelancer has been notified by email.')
    return redirect('project_detail', pk=bid.project.pk)