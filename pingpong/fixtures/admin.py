from django.contrib import admin
from .models import League, Player, Participants, OneGame, SetTable


class SetTableAdmin(admin.ModelAdmin):
    list_display = SetTable.__slots__


admin.site.register(League)
admin.site.register(Player)
admin.site.register(Participants)
admin.site.register(OneGame)
admin.site.register(SetTable, SetTableAdmin)
