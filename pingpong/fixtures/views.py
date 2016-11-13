from django.shortcuts import render, redirect, reverse
from fixtures.models import *


# viewとは関係なし
def createmixture(onegame):  # templateを楽にわかりやすく書くための関数
    mixedls = []
    for game in onegame:
        p1, p2 = game.player_A, game.player_B
        p1set, p2set = game.A_win_set, game.B_win_set
        p1gains, p2gains = get_ABgain_from_onegame(game, "A"), get_ABgain_from_onegame(game, "B")
        A_win_question = game.is_A_win

        # [((A, Aセット), (B, Bセット)), (Aゲインリスト, Bゲインリスト), A勝ちか]
        mixedls.append([((p1, p1set), (p2, p2set)), (p1gains, p2gains), A_win_question])
    return mixedls


def get_ABgain_from_onegame(game, letter):
    filter_ = SetTable.objects.filter
    dct = {"A": [x.A_gain for x in filter_(game_No=game)], "B": [x.B_gain for x in filter_(game_No=game)]}
    padding = game.A_win_set + game.B_win_set
    return dct[letter] + [0 for i in range(5 - padding)]


# 以下views
def index(request):
    return render(request, "fixtures/index.html", {
        "league": League.objects.all(),
    })


def detail(request, pk):
    # 以下データベース更新
    for g in OneGame.objects.all():
        g.calc_set_num()
        g.save()
    for p in Player.objects.all():
        p.calc_gain_num()
        p.calc_various_num()
        p.save()
    # 更新ここまで

    league = League.objects.get(pk=pk)
    participants = Participants.objects.filter(league=league)
    onegame = OneGame.objects.filter(league=league)
    mixedls = createmixture(onegame)
    settable = [SetTable.objects.filter(game_No=og) for og in onegame]

    return render(request, "fixtures/detail.html", {
        "players": [x.player for x in participants],
        "league": league,
        "onegame": onegame,
        "mixedls": mixedls,
        "gameset": sorted([x for x in SetTable.objects.all()], key=lambda x: x.set_No),
        "five": [1,2,3,4,5],
    })


def league_regist(request):
    return render(request, "fixtures/league_regist.html")


def league_complete(request):
    return redirect(reverse("league:index"))
