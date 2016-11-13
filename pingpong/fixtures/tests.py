from django.test import TestCase, RequestFactory
from fixtures.models import *


# Create your tests here.
class TestChange(TestCase):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        for game in OneGame.objects.all():
            game.calc_set_num()
        self.p = Player.objects.get(p_name="あ")
        self.p.calc_gain_num()
        self.p.calc_various_num()

    def setUp(self):
        self.factory = RequestFactory()

    def test_change_playerdata(self):
        self.assertEqual(self.p.total_win_points, 35)

    def test_set_num(self):
        ws = 0
        ls = 0
        for game in OneGame.objects.filter(player_A=self.p.pk):
            ws += game.A_win_set
            ls += game.B_win_set
        for game in OneGame.objects.filter(player_B=self.p.pk):
            ws += game.B_win_set
            ls += game.A_win_set

        self.assertEqual(ws, 2)
        self.assertEqual(ls, 1)
