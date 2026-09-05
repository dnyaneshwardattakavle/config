from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Profile
from requests_app.models import Request


# Home test
def accounts(request):
    return HttpResponse("this is account app")


# Signup
def signup(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect('/')

    return render(request, 'signup.html')


# Login
def login_view(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('/')

        else:

            return HttpResponse("Invalid username or password")

    return render(request, 'login.html')


# Logout
def logout_view(request):

    logout(request)

    return redirect('/accounts/login/')


# Profile
@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':

        profile.bio = request.POST['bio']
        profile.skills = request.POST['skills']

        # Profile photo - optional
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']

        profile.save()

        return redirect('/')

    return render(
        request,
        'profile.html',
        {'profile': profile}
    )


# All Users (Profiles)
def all_users(request):

    users = Profile.objects.all()

    return render(
        request,
        'all_users.html',
        {'users': users}
    )


# Users list (for sending request)
@login_required
def users_list(request):

    users = User.objects.exclude(
        id=request.user.id
    )

    return render(
        request,
        'users.html',
        {'users': users}
    )


# Send Request
@login_required
def send_request(request, user_id):

    receiver = get_object_or_404(
        User,
        id=user_id
    )

    if request.user == receiver:

        return HttpResponse(
            "You cannot send request to yourself."
        )

    if request.method == 'POST':

        message = request.POST.get(
            'message',
            ''
        )

        existing_request = Request.objects.filter(
            sender=request.user,
            receiver=receiver,
            status='pending'
        ).exists()

        if existing_request:

            return HttpResponse(
                "You already have a pending request with this user."
            )

        Request.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message
        )

        return redirect('/accounts/users/')

    return render(
        request,
        'send_request.html',
        {'receiver': receiver}
    )


# Inbox
@login_required
def inbox(request):

    received_requests = Request.objects.filter(
        receiver=request.user
    )

    sent_requests = Request.objects.filter(
        sender=request.user
    )

    return render(
        request,
        'inbox.html',
        {
            'received_requests': received_requests,
            'sent_requests': sent_requests,
        }
    )


# Accept / Reject
@login_required
def update_request(request, req_id, action):

    req = get_object_or_404(
        Request,
        id=req_id,
        receiver=request.user
    )

    if req.status != 'pending':

        return redirect('/accounts/inbox/')

    if action == 'accept':

        req.status = 'accepted'

    elif action == 'reject':

        req.status = 'rejected'

    req.save()

    return redirect('/accounts/inbox/')


# Connections
@login_required
def connections(request):

    sent = Request.objects.filter(
        sender=request.user,
        status='accepted'
    ).values_list(
        'receiver',
        flat=True
    )

    received = Request.objects.filter(
        receiver=request.user,
        status='accepted'
    ).values_list(
        'sender',
        flat=True
    )

    connection_ids = list(sent) + list(received)

    connections = User.objects.filter(
        id__in=connection_ids
    )

    return render(
        request,
        'connections.html',
        {
            'connections': connections
        }
    )