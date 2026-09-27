from django.contrib import admin
from .models import Club, Membership, Pick, Comment, Nomination, Vote

# Register your models here.


admin.site.register(Club)
admin.site.register(Membership)
admin.site.register(Pick)
admin.site.register(Comment)
admin.site.register(Nomination)
admin.site.register(Vote)

