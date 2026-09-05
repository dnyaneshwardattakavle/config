from django.urls import path
from . import views

urlpatterns = [

    path('', views.accounts),

    path('signup/', views.signup, name='signup'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile, name='profile'),

    path('users/', views.all_users, name='all_users'),

    path(
        'send-request/<int:user_id>/',
        views.send_request,
        name='send_request'
    ),

    path('inbox/', views.inbox, name='inbox'),

    path(
        'request/<int:req_id>/<str:action>/',
        views.update_request,
        name='update_request'
    ),

    path(
        'connections/',
        views.connections,
        name='connections'
    ),
]