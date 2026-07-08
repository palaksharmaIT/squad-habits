from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone
from .models import Squad, SquadMember, InviteLink
import re
from habits.models import Habit, HabitLog



@login_required
def squad_list(request):
    # Fetch squads where the user is a member
    memberships = SquadMember.objects.filter(
        user=request.user
    ).select_related('squad')

    squads = [membership.squad for membership in memberships]

    return render(request, 'squads/squad_list.html', {
        'squads': squads
    })


@login_required
def create_squad(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(request, "Squad name is required.")

        elif not re.fullmatch(r"[A-Za-z ]+", name):
            messages.error(
                request,
                "Squad name can contain only letters and spaces."
            )

        else:
            squad = Squad.objects.create(
                name=name,
                admin=request.user
            )

            # Add creator as first member
            SquadMember.objects.create(
                squad=squad,
                user=request.user
            )

            messages.success(request, "Squad created successfully.")
            return redirect("squad_list")

    return render(request, "squads/create_squad.html")




@login_required
def generate_invite(request, squad_id):
    squad = get_object_or_404(Squad, id=squad_id)

    # Only admin can generate invite
    if squad.admin != request.user:
        return HttpResponse("Permission Denied", status=403)

    # Reuse existing valid invite if available
    invite = InviteLink.objects.filter(
        squad=squad,
        expires_at__gt=timezone.now()
    ).first()

    # Otherwise create a new invite
    if not invite:
        invite = InviteLink.objects.create(
            squad=squad
        )

    invite_url = request.build_absolute_uri(
        reverse("join_squad", args=[invite.token])
    )

    return render(request, "squads/invite.html", {
        "invite_url": invite_url
    })


@login_required
def join_squad(request, token):
    invite = get_object_or_404(
        InviteLink,
        token=token
    )

    if not invite.is_valid():
        return HttpResponse("Invite link has expired.", status=400)

    SquadMember.objects.get_or_create(
        squad=invite.squad,
        user=request.user
    )

    messages.success(
        request,
        f"You joined '{invite.squad.name}' successfully!"
    )

    return redirect(
        "squad_detail",
        squad_id=invite.squad.id
    )


@login_required
def create_habit(request, squad_id):
    squad = get_object_or_404(Squad, id=squad_id)

    # Only squad admin can create habits
    if squad.admin != request.user:
        return HttpResponse("Permission Denied", status=403)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()

        if not title:
            messages.error(request, "Habit title is required.")
        else:
            Habit.objects.create(
                squad=squad,
                title=title,
                created_by=request.user
            )

            messages.success(request, "Habit created successfully.")
            return redirect("squad_detail", squad_id=squad.id)

    return render(request, "habits/create_habit.html", {
        "squad": squad
    })



@login_required
def mark_habit_done(request, habit_id):

    print("MARK DONE VIEW CALLED")
    print(request.method)

    habit = get_object_or_404(Habit, id=habit_id)

    # Check user is member of squad
    if not SquadMember.objects.filter(
        squad=habit.squad,
        user=request.user
    ).exists():
        return HttpResponse("Permission Denied", status=403)

    # Mark today's habit as done
    HabitLog.objects.update_or_create(
        habit=habit,
        user=request.user,
        date=timezone.now().date(),
        defaults={
            "is_done": True
        }
    )

    print("Habit Saved Successfully")

    messages.success(request, "Habit marked as completed!")

    return redirect("squad_detail", squad_id=habit.squad.id)

@login_required
def squad_detail(request, squad_id):
    squad = get_object_or_404(Squad, id=squad_id)

    # Allow only squad members
    if not SquadMember.objects.filter(
        squad=squad,
        user=request.user
    ).exists():
        return HttpResponse("Permission Denied", status=403)

    members = SquadMember.objects.filter(
        squad=squad
    ).select_related("user")

    habits = Habit.objects.filter(
        squad=squad
    )

    completed_habits = HabitLog.objects.filter(
        user=request.user,
        date=timezone.now().date(),
        is_done=True
    ).values_list("habit_id", flat=True)

    return render(request, "squads/squad_detail.html", {
        "squad": squad,
        "members": members,
        "habits": habits,
        "completed_habits": completed_habits,
        "is_admin": squad.admin == request.user,
    })


@login_required
def join_squad(request, token):

    invite = get_object_or_404(
        InviteLink,
        token=token
    )

    if not invite.is_valid():
        return HttpResponse("Invite link has expired.", status=400)

    # Already joined
    if SquadMember.objects.filter(
        squad=invite.squad,
        user=request.user
    ).exists():

        messages.info(request, "You are already a member.")
        return redirect("squad_detail", squad_id=invite.squad.id)

    if request.method == "POST":

        SquadMember.objects.create(
            squad=invite.squad,
            user=request.user
        )

        messages.success(
            request,
            f"You joined '{invite.squad.name}' successfully!"
        )

        return redirect(
            "squad_detail",
            squad_id=invite.squad.id
        )

    return render(
        request,
        "squads/join_squad.html",
        {
            "squad": invite.squad
        }
    )