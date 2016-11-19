from django.shortcuts import render, redirect, reverse
from fixtures.models import *
from django.views.generic.edit import CreateView


# viewとは関係なし
# templateを楽にわかりやすく書くための関数のつもり
def createmixture(onegame):
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


def calc_various_num(player):
    """
     選手の勝ち試合数, 負け試合数, 勝利セット数, 敗北セット数, セット率を計算
     このへんとても冗長なのでなんとかしたい
    """
    alike_wn = 0  # win_num
    alike_ln = 0  # lose_num
    alike_twsn = 0  # total_win_set_num
    alike_tlsn = 0  # total_lose_set_num
    alike_wn, alike_ln, alike_twsn, alike_tlsn = various_num_asA(player)
    alike_wn, alike_ln, alike_twsn, alike_tlsn = tuple(map(
        lambda x, y: x + y, various_num_asB(player), [alike_wn, alike_ln, alike_twsn, alike_tlsn]
    ))

    player.win_num = alike_wn
    player.lose_num = alike_ln
    player.total_win_set_num = alike_twsn
    player.total_lose_set_num = alike_tlsn
    try:
        player.set_rate = alike_twsn/(alike_tlsn + alike_twsn)*100
    except ZeroDivisionError:
        player.set_rate = 0
    player.save()


def various_num_asA(player):
    wn, ln, wsn, lsn = 0, 0, 0, 0  # win_num, lose_num, total_win_set_num, total_lose_set_num
    for game in OneGame.objects.filter(player_A=player):
        a_wins = game.A_win_set  # A獲得セット数
        b_wins = game.B_win_set  # B獲得セット数(A喪失セット数)

        wsn += a_wins
        lsn += b_wins
        if (a_wins == 3 or b_wins == 3) and a_wins > b_wins:
            wn += 1
        elif (a_wins == 3 or b_wins == 3) and a_wins < b_wins:
            ln += 1
    return wn, ln, wsn, lsn


def various_num_asB(player):
    wn, ln, wsn, lsn = 0, 0, 0, 0
    for game in OneGame.objects.filter(player_B=player):
        a_wins = game.B_win_set
        b_wins = game.A_win_set

        wsn += a_wins
        lsn += b_wins
        if (a_wins == 3 or b_wins == 3) and a_wins > b_wins:
            wn += 1
        elif (a_wins == 3 or b_wins == 3) and a_wins < b_wins:
            ln += 1
    return wn, ln, wsn, lsn


def calc_gain_num(player):
    """ total point数を計算 """
    alike_twp = 0
    alike_tlp = 0
    alike_twp, alike_tlp = gain_num_asA(player)
    alike_twp, alike_tlp = tuple(map(
        lambda x, y: x + y, gain_num_asB(player), [alike_twp, alike_tlp]
    ))

    player.total_win_points = alike_twp
    player.total_lose_points = alike_tlp
    try:
        player.points_rate = alike_twp/(alike_tlp + alike_twp)*100
    except ZeroDivisionError:
        player.points_rate = 0
    player.save()


def gain_num_asA(player):
    wp, lp = 0, 0
    for game in OneGame.objects.filter(player_A=player):
        for gain in SetTable.objects.filter(game_No=game):
            wp += gain.A_gain
            lp += gain.B_gain
    return wp, lp


def gain_num_asB(player):
    wp, lp = 0, 0
    for game in OneGame.objects.filter(player_B=player):
        for gain in SetTable.objects.filter(game_No=game):
            wp += gain.B_gain
            lp += gain.A_gain
    return wp, lp


def calc_set_num(game):
    """ OneGameの得点を計算 """
    ws, ls = 0, 0
    for gain in SetTable.objects.filter(game_No=game):
        if gain.A_gain > gain.B_gain:
            ws += 1
        else:
            ls += 1
    game.A_win_set = ws
    game.B_win_set = ls

    game.is_A_win = True if (ws == 3 or ls == 3) and (ws > ls) else False
    game.save()


def AvsBatleague(game, league, A, B):
    """ OneGameに諸々を設定 """
    game.league = league
    game.player_A = A
    game.player_B = B
    game.save()


""" 順位を計算 """
def calc_rank(league):
    players = [x.player for x in Participants.objects.filter(league=league)]
    if sum([int(x.win_num) + int(x.lose_num) for x in players]) == 0:
        return
    tmp = sorted(players, key=lambda x: x.points_rate, reverse=True)  # ポイント獲得の降順でソート
    tmp = sorted(tmp, key=lambda x: x.set_rate, reverse=True)  # セット率の降順でソート
    tmp = sorted(tmp, key=lambda x: x.win_num, reverse=True)  # 勝ち数の降順でソート
    for i, p in enumerate(tmp):
        p.rank = i + 1
        p.save()

    n = len(players)
    if sum([int(x.win_num) + int(x.lose_num) for x in players]) == n*(n-1):
        league.whole_winner = tmp[0]
        league.save()


def update_database(league):
    # 以下データベース更新
    for g in OneGame.objects.filter(league=league):
        calc_set_num(g)
    for p in [x.player for x in Participants.objects.filter(league=league)]:
        calc_gain_num(p)
        calc_various_num(p)
    calc_rank(league)
    # 更新ここまで


# 以下views
def index(request):
    return render(request, "fixtures/index.html", {
        "league": League.objects.all(),
    })


def detail(request, pk):
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
    })


def player_regist(request, pk):
    league = League.objects.get(pk=int(pk))
    return render(request, "fixtures/player_regist.html", {
        "pk": pk,
        "number": range(league.num_of_participant),
    })


def player_complete(request):
    # 選手の名前をformから受け取る
    if request.method == "POST":
        league = League.objects.get(pk=int(request.POST["pk"]))

        tmp = []
        for ky, val in request.POST.items():
            if ky == "pk" or ky == "csrfmiddlewaretoken":  # csrfもhiddenで渡されているので
                continue
            new_player = Player()
            new_participant = Participants()
            new_player.p_name = val
            new_player.save()

            new_participant.player = new_player  # Participantsに選手を登録
            new_participant.league = league  # Participantsにリーグ登録
            new_participant.save()
            tmp.append(new_player)

        tmp = sorted(tmp, key=lambda x: x.p_name)  # 名前の昇順でソート
        while tmp:
            list(map(lambda x: AvsBatleague(OneGame(), league, tmp[0], x), tmp[1:]))  # 考えうるplayer同士のOneGameを作成
            tmp.remove(tmp[0])
        update_database(league)

    return redirect(reverse("league:index"))


def league_regist(request):
    return render(request, "fixtures/league_regist.html")


def league_complete(request):
    # 大会に関する情報をformから受け取る
    if request.method == "POST":
        newleague = League()
        post = request.POST
        newleague.league_name = post["league_name"]
        newleague.league_date = post["league_date"]
        newleague.num_of_participant = post["league_participant"]
        newleague.save()
        return redirect(reverse("league:p_regist", kwargs={"pk": newleague.pk}))
    else:
        return redirect(reverse("league:index"))


def redraw_league_table(request, pk):
    # formからの得点データを評価してリーグ表を更新
    csrf_label = "csrfmiddlewaretoken"
    league = League.objects.get(pk=pk)
    games = OneGame.objects.filter(league=league)
    # 必要なデータだけを取捨選択
    havepoints = [
        (ky.split("/"), val) for ky, val in request.POST.items() \
        if (ky not in [csrf_label, "updatedb"] and val != "0")
    ]
    get = SetTable.objects.get
    # この辺クソすぎるのでなんとかしたい
    for ky, val in sorted(havepoints, key=lambda x: x[0][3]):
        # ky = [("a" or "b", player_A, player_B, set_No)]  val = score of a or b
        for g in games:
            try:
                st = get(game_No=g, set_No=int(ky[3]))  # まだ作られていない可能性がある
            except Exception:
                st = SetTable()
                st.game_No = g
                st.set_No = int(ky[3])

            if ky[:3] == ["a", g.player_A.p_name, g.player_B.p_name]:
                st.A_gain = int(val)
                st.save()
            elif ky[:3] == ["b", g.player_A.p_name, g.player_B.p_name]:
                st.B_gain = int(val)
                st.save()

    update_database(league)
    return redirect(reverse("league:detail" , kwargs={"pk": pk}))
