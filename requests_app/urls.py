from django.urls import path
from . import views


urlpatterns = [

    path(
        'users/',
        views.users_list,
        name='users'
    ),

    path(
        'send_request/<int:user_id>/',
        views.send_request,
        name='send_request'
    ),

    path(
        'inbox/',
        views.inbox,
        name='inbox'
    ),

    path(
        'accept/<int:id>/',
        views.accept_request,
        name='accept'
    ),

    path(
        'reject/<int:id>/',
        views.reject_request,
        name='reject'
    ),

    path(
        'chat/<int:user_id>/',
        views.chat,
        name='chat'
    ),

    path(
        'search/',
        views.search_users,
        name='search_users'
    ),

    path(
        'profile/<int:user_id>/',
        views.user_profile,
        name='user_profile'
    ),

    path(
        'recommended/',
        views.recommended_users,
        name='recommended_users'
    ),

    path(
        'connections/',
        views.connections,
        name='connections'
    ),
]