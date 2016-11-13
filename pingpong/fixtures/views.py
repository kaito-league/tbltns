from django.shortcuts import render
from fixtures.models import *


# Create your views here.
def index(request):
    return render(request, "fixtures/index.html", {
        "league": League.objects.all(),
    })


def detail(request, pk):
    for g in OneGame.objects.all():
        g.calc_set_num()
        g.save()
    for p in Player.objects.all():
        p.calc_gain_num()
        p.calc_various_num()
        p.save()
    league = League.objects.get(pk=pk)
    participants = Participants.objects.filter(league=league)
    onegame = OneGame.objects.filter(league=league)
    settable = [SetTable.objects.filter(game_No=og) for og in onegame]
    return render(request, "fixtures/detail.html", {
        "players": [x.player for x in participants],
        "league": league,
        "onegame": onegame,
        "settable": settable,
    })


def regist(request):
    return render(request, "fixtures/league_regist.html")
