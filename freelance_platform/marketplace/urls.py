from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='marketplace/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/create/', views.create_project, name='create_project'),
    path('my-projects/', views.my_projects, name='my_projects'),
    path('project/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('bid/<int:bid_id>/accept/', views.accept_bid, name='accept_bid'),
]