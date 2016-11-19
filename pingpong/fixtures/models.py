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
