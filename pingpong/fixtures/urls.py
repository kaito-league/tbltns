from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^league-table/(?P<pk>\d+)', views.detail, name="detail"),
    url(r'^league-regist', views.league_regist, name="regist"),
    url(r'^league-complete', views.league_complete, name="l_comp"),
]
