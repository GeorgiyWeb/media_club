from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    # auth
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # all related to project
    path("clubs/create/", views.club_create, name="club_create"),
    path("clubs/vote/<int:nomination_id>/", views.vote, name="vote"),
    path("clubs/comment/<int:pick_id>/", views.create_comment, name="create_comment"),
    path("clubs/<int:id>/", views.club_detail, name="club_detail"),
    path("clubs/<int:id>/join/", views.join_club, name="join_club"),
    path("clubs/<int:id>/leave/", views.leave_club, name="leave_club"),
    path("clubs/<int:id>/nominations/", views.nominations, name="nominations_list"),
    path("clubs/<int:id>/nominations/create/", views.create_nomination, name="create_nomination"),
    path("clubs/<int:id>/close/", views.close_pick, name="close_pick"),

    # profile page
    path("profile/<str:username>/", views.profile, name="profile"),
]