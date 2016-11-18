from django.db import models


class Player(models.Model):
    """ 大会参加者の勝敗データを保持するテーブル """
    p_name = models.CharField("参加者名", max_length=20)
    win_num = models.PositiveIntegerField("勝ち試合数", default=0)  # PositiveSmallIntegerFieldでもよいと思う
    lose_num = models.PositiveIntegerField("負け試合数", default=0)
    total_win_set_num = models.PositiveSmallIntegerField("勝利セット数", default=0)
    total_lose_set_num = models.PositiveSmallIntegerField("敗北セット数", default=0)
    set_rate = models.FloatField("セット率", default=0.0)  # or DecimalField
    total_win_points = models.PositiveIntegerField("総獲得得点", default=0)
    total_lose_points = models.PositiveIntegerField("総喪失得点", default=0)
    points_rate = models.FloatField("得点率" , default=0.0)  # or DecimalField
    rank = models.PositiveSmallIntegerField("順位", default=1)

    __slots__ = [
        "p_name", "win_num", "lose_num", "total_win_set_num", "total_lose_set_num",
        "set_rate", "total_win_points", "total_lose_points", "points_rate",
    ]

    def calc_various_num(self):
        """
         勝ち試合数, 負け試合数, 勝利セット数, 敗北セット数, セット率を計算
         このへんとても冗長なのでなんとかしたい
        """

        self.alike_win_num = 0
        self.alike_lose_num = 0
        self.alike_total_win_set_num = 0
        self.alike_total_lose_set_num = 0
        self.__various_num_asA()
        self.__various_num_asB()

        self.win_num = self.alike_win_num
        self.lose_num = self.alike_lose_num
        self.total_win_set_num = self.alike_total_win_set_num
        self.total_lose_set_num = self.alike_total_lose_set_num
        try:
            self.set_rate = self.total_win_set_num/(self.total_lose_set_num + self.total_win_set_num)*100
        except ZeroDivisionError:
            self.set_rate = 0

    def __various_num_asA(self):
        wn, ln, wsn, lsn = 0, 0, 0, 0  # win_num, lose_num, total_win_set_num, total_lose_set_num
        for game in OneGame.objects.filter(player_A=self):
            a_wins = game.A_win_set  # A獲得セット数
            b_wins = game.B_win_set  # B獲得セット数(A喪失セット数)

            wsn += a_wins
            lsn += b_wins
            if (a_wins == 3 or b_wins == 3) and a_wins > b_wins:
                wn += 1
            elif (a_wins == 3 or b_wins == 3) and a_wins < b_wins:
                ln += 1
        self.alike_win_num += wn  # Aの勝ち数を加算
        self.alike_lose_num += ln  # Aの負け数を加算
        self.alike_total_win_set_num += wsn
        self.alike_total_lose_set_num += lsn

    def __various_num_asB(self):
        wn, ln, wsn, lsn = 0, 0, 0, 0
        for game in OneGame.objects.filter(player_B=self):
            a_wins = game.B_win_set
            b_wins = game.A_win_set

            wsn += a_wins
            lsn += b_wins
            if (a_wins == 3 or b_wins == 3) and a_wins > b_wins:
                wn += 1
            elif (a_wins == 3 or b_wins == 3) and a_wins < b_wins:
                ln += 1
        self.alike_win_num += wn
        self.alike_lose_num += ln
        self.alike_total_win_set_num += wsn
        self.alike_total_lose_set_num += lsn

    def calc_gain_num(self):
        """ total point数を計算 """
        self.alike_total_win_points = 0
        self.alike_total_lose_points = 0
        self.__gain_num_asA()
        self.__gain_num_asB()

        self.total_win_points = self.alike_total_win_points
        self.total_lose_points = self.alike_total_lose_points
        try:
            self.points_rate = self.total_win_points/(self.total_lose_points + self.total_win_points)*100
        except ZeroDivisionError:
            self.points_rate = 0

    def __gain_num_asA(self):
        wp, lp = 0, 0
        # 二重ループは嫌や...
        for game in OneGame.objects.filter(player_A=self):
            for gain in SetTable.objects.filter(game_No=game):
                wp += gain.A_gain
                lp += gain.B_gain
        self.alike_total_win_points += wp
        self.alike_total_lose_points += lp

    def __gain_num_asB(self):
        wp, lp = 0, 0
        # 二重ループは嫌や...
        for game in OneGame.objects.filter(player_B=self):
            for gain in SetTable.objects.filter(game_No=game):
                wp += gain.B_gain
                lp += gain.A_gain
        self.alike_total_win_points += wp
        self.alike_total_lose_points += lp

    def __str__(self):
        return self.p_name


# Create your models here.
class League(models.Model):
    """ 大会の情報 """
    league_name = models.CharField("リーグの名前", max_length=20)
    league_date = models.DateField("大会年月日")
    num_of_participant = models.PositiveSmallIntegerField("参加人数")
    whole_winner = models.ForeignKey(Player, blank=True, null=True)

    def __str__(self):
        return self.league_name


class OneGame(models.Model):
    """ ある試合のデータ """
    league = models.ForeignKey(League)
    player_A = models.ForeignKey(Player, related_name="player_A")  # Aが自分
    player_B = models.ForeignKey(Player, related_name="player_B")  # Bは敵, という設定
    A_win_set = models.PositiveSmallIntegerField("A選手獲得セット数", default=0)
    B_win_set = models.PositiveSmallIntegerField("B選手獲得セット数", default=0)
    is_A_win = models.NullBooleanField("Aが勝ったか", blank=True, null=True)

    def get_SetTable(self):
        """ for calc_gain_num """
        return SetTable.objects.filter(game_No=self)

    def calc_set_num(self):
        ws, ls = 0, 0
        for gain in SetTable.objects.filter(game_No=self):
            if gain.A_gain > gain.B_gain:
                ws += 1
            else:
                ls += 1
        self.A_win_set = ws
        self.B_win_set = ls

        if self.A_win_set == 3 or self.B_win_set == 3:
            self.which_win()

    def which_win(self):
        self.is_A_win = True if self.A_win_set > self.B_win_set else False

    def AvsBatleague(self, league, A, B):
        self.league = league
        self.player_A = A
        self.player_B = B
        self.save()

    def __str__(self):
        return "%s vs %s"%(self.player_A.p_name, self.player_B.p_name)


class SetTable(models.Model):
    game_No = models.ForeignKey(OneGame)
    set_No = models.PositiveSmallIntegerField("第nセット", default=0)
    A_gain = models.PositiveSmallIntegerField("A獲得得点", default=0)
    B_gain = models.PositiveSmallIntegerField("B獲得得点", default=0)

    __slots__ = ["__str__", "game_No", "set_No", "A_gain", "B_gain"]

    def __str__(self):
        return self.game_No.league.league_name


class Participants(models.Model):
    """
    大会参加者の名前だけを保持するテーブル
    このままだと league:player が1:1の関係でレコードが作られる. これだと同じleagueが何個も登場することに...
    個人的には league:[player, player, ..., player] という感じがいい.
    jsonを使えばできるっぽい > http://stackoverflow.com/questions/22340258/django-list-field-in-model
    """
    league = models.ForeignKey(League)
    player = models.ForeignKey(Player)

    __slots__ = ["league", "player"]

    def __str__(self):
        return self.player.p_name
