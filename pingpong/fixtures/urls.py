from django.conf.urls import url, include

from . import views


urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^league-table/(?P<pk>\d+)', views.detail, name="detail"),
    url(r'^league-regist', views.regist, name="regist"),
]
