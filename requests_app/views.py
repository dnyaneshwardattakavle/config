from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from .models import Request, Message
from accounts.models import Profile


User = get_user_model()


# ==========================================
# CONNECTION STATUS
# ==========================================

def get_connection_status(current_user, other_user):

    if Request.objects.filter(
        sender=current_user,
        receiver=other_user,
        status='accepted'
    ).exists() or Request.objects.filter(
        sender=other_user,
        receiver=current_user,
        status='accepted'
    ).exists():

        return 'connected'

    if Request.objects.filter(
        sender=current_user,
        receiver=other_user,
        status='pending'
    ).exists():

        return 'sent'

    if Request.objects.filter(
        sender=other_user,
        receiver=current_user,
        status='pending'
    ).exists():

        return 'received'

    return 'none'


# ==========================================
# USERS
# ==========================================

@login_required
def users_list(request):
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'users.html', {
        'users': users
    })


# ==========================================
# SEND REQUEST
# ==========================================

@login_required
def send_request(request, user_id):

    receiver = get_object_or_404(
        User,
        id=user_id
    )

    # Cannot send request to yourself
    if receiver == request.user:
        return HttpResponse(
            "You cannot send request to yourself."
        )

    # Already connected
    already_connected = Request.objects.filter(
        sender=request.user,
        receiver=receiver,
        status='accepted'
    ).exists() or Request.objects.filter(
        sender=receiver,
        receiver=request.user,
        status='accepted'
    ).exists()

    if already_connected:
        return HttpResponse(
            "You are already connected."
        )

    # Already pending request
    pending_request = Request.objects.filter(
        sender=request.user,
        receiver=receiver,
        status='pending'
    ).exists()

    if pending_request:
        return HttpResponse(
            "Request already sent."
        )

    # Opposite side already sent request
    received_request = Request.objects.filter(
        sender=receiver,
        receiver=request.user,
        status='pending'
    ).exists()

    if received_request:
        return redirect('inbox')

    if request.method == 'POST':

        message = request.POST.get(
            'message',
            ''
        )

        Request.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message
        )

        return redirect('inbox')

    return render(request, 'send_request.html', {
        'receiver': receiver
    })


# ==========================================
# INBOX
# ==========================================

@login_required
def inbox(request):

    received_requests = Request.objects.filter(
        receiver=request.user
    ).order_by('-created_at')

    sent_requests = Request.objects.filter(
        sender=request.user
    ).order_by('-created_at')

    return render(request, 'inbox.html', {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    })

# ==========================================
# ACCEPT REQUEST
# ==========================================

@login_required
def accept_request(request, id):

    req = get_object_or_404(
        Request,
        id=id,
        receiver=request.user,
        status='pending'
    )

    req.status = 'accepted'
    req.save()

    return redirect('inbox')


# ==========================================
# REJECT REQUEST
# ==========================================

@login_required
def reject_request(request, id):

    req = get_object_or_404(
        Request,
        id=id,
        receiver=request.user,
        status='pending'
    )

    req.status = 'rejected'
    req.save()

    return redirect('inbox')


# ==========================================
# CONNECTIONS
# ==========================================

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

    user_ids = list(sent) + list(received)

    users = User.objects.filter(
        id__in=user_ids
    )

    return render(request, 'connections.html', {
        'connections': users
    })


# ==========================================
# CHAT
# ==========================================

@never_cache
@login_required
def chat(request, user_id):

    receiver = get_object_or_404(
        User,
        id=user_id
    )

    # Chat only after connection
    is_friend = Request.objects.filter(
        sender=request.user,
        receiver=receiver,
        status='accepted'
    ).exists() or Request.objects.filter(
        sender=receiver,
        receiver=request.user,
        status='accepted'
    ).exists()

    if not is_friend:
        return HttpResponse(
            "You can only chat after request is accepted."
        )

    messages = Message.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    ).order_by('timestamp')

    if request.method == 'POST':

        text = request.POST.get(
            'text',
            ''
        ).strip()

        if text:

            Message.objects.create(
                sender=request.user,
                receiver=receiver,
                text=text
            )

        return redirect(
            'chat',
            user_id=receiver.id
        )

    return render(request, 'chat.html', {
        'receiver': receiver,
        'messages': messages
    })


# ==========================================
# SEARCH
# ==========================================

@login_required
def search_users(request):
    query = request.GET.get('q', '').strip()

    users = Profile.objects.exclude(user=request.user)

    if query:
        users = users.filter(skills__icontains=query)

    print("SEARCH:", query)
    print("RESULTS:", list(users.values('user__username', 'skills')))

    return render(request, 'search_users.html', {
        'users': users,
        'query': query,
    })

# ==========================================
# USER PROFILE
# ==========================================

@login_required
def user_profile(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id
    )

    profile, created = Profile.objects.get_or_create(
        user=user
    )

    status = get_connection_status(
        request.user,
        user
    )

    return render(request, 'user_profile.html', {
        'user_profile': user,
        'profile': profile,
        'status': status
    })


# ==========================================
# RECOMMENDED USERS
# ==========================================

@login_required
def recommended_users(request):

    current_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    my_skills = [
        skill.strip().lower()
        for skill in current_profile.skills.split(',')
        if skill.strip()
    ]

    recommended = []

    profiles = Profile.objects.exclude(
        user=request.user
    )

    for profile in profiles:

        # Skills ko comma ke according separate karna
        skills_list = [
            skill.strip()
            for skill in profile.skills.split(',')
            if skill.strip()
        ]

        # Comparison ke liye lowercase skills
        other_skills = [
            skill.lower()
            for skill in skills_list
        ]

        common_skills = set(my_skills) & set(other_skills)

        if common_skills:

            status = get_connection_status(
                request.user,
                profile.user
            )

            recommended.append({
                'profile': profile,
                'skills_list': skills_list,
                'common_skills': common_skills,
                'match_count': len(common_skills),
                'status': status
            })

    recommended.sort(
        key=lambda x: x['match_count'],
        reverse=True
    )

    return render(request, 'recommended_users.html', {
        'recommended_users': recommended
    })