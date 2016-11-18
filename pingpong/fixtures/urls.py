from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^league-table/(?P<pk>\d+)', views.detail, name="detail"),
    url(r'^regist/league', views.league_regist, name="l_regist"),
    url(r'^complete/league', views.league_complete, name="l_comp"),
    url(r'^regist/player(?P<pk>\d+)', views.player_regist, name="p_regist"),
    url(r'^complete/player', views.player_complete, name="p_comp"),
    url(r'^redraw/(?P<pk>\d+)', views.redraw_league_table, name="redraw_ltable"),
]
