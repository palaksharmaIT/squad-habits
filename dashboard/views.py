
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from squads.models import SquadMember


def home(request):
    return render(request, 'dashboard/home.html')


@login_required
def home(request):

    memberships = SquadMember.objects.filter(
        user=request.user
    ).select_related("squad")

    squads = [membership.squad for membership in memberships]

    return render(request, "dashboard/home.html", {
        "squads": squads,
    })

