from django.contrib import admin
from .models import League, Player, Participants, OneGame, SetTable


class SetTableAdmin(admin.ModelAdmin):
    list_display = SetTable.__slots__


class LeagueAdmin(admin.ModelAdmin):
    list_display = ["pk", "league_name"]


class PlayerAdmin(admin.ModelAdmin):
    list_display = ["pk"] + Player.__slots__


class ParticipantsAdmin(admin.ModelAdmin):
    list_display = ["pk"] + Participants.__slots__


admin.site.register(League, LeagueAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Participants, ParticipantsAdmin)
admin.site.register(OneGame)
admin.site.register(SetTable, SetTableAdmin)
