from django.test import TestCase, RequestFactory
from django.shortcuts import resolve_url
from fixtures.models import *


# Create your tests here.
class RegistTest(TestCase):
    def test_regist_player(self):
        response = self.client.get(resolve_url("league:p_regist", pk=10))  # エラー
        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.context["pk"])
        self.assertEqual(6, response.context["number"])
