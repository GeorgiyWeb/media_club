from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Club, Nomination, Pick, Membership
from .forms import ClubCreateForm

# Create your views here.


def index(request):
    category = request.GET.get("category")
    
    if category:
        clubs = Club.objects.filter(category=category)
    
    else:
        clubs = Club.objects.all()
        
    
    return render(request, "clubs/index.html", {'clubs' : clubs})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    clubs = Club.objects.filter(memberships__user = user)
    created_clubs = user.created_clubs.all()
    nominations = user.authored_nominations.count()
    
    return render(request, "clubs/profile.html", {'profile_user' : user,
                                'clubs' : clubs,
                                'created_clubs' : created_clubs,
                                'nominations' : nominations})


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("index")
            
    else:   
        form = UserCreationForm()
        
    return render(request, "clubs/register.html", {'form' : form})


@login_required
def club_create(request):
    if request.method == "POST":
        form = ClubCreateForm(request.POST)

        if form.is_valid():
            club = form.save(commit=False)
            club.creator = request.user
            club.save()

          
            Pick.objects.create(
                title=form.cleaned_data['pick_title'],
                creator=form.cleaned_data['pick_creator'],
                club=club,
                author=request.user,
                is_active=True,
            )

           
            Membership.objects.create(user=request.user, club=club)

            return redirect("club_detail", id=club.id)

    else:
        form = ClubCreateForm()

    return render(request, "clubs/club_create.html", {"form": form})
            

def vote(request):
    pass

def create_comment(request):
    pass

def club_detail(request, id):
    club = get_object_or_404(Club, id=id)
    pick = club.picks.filter(is_active=True).first()
    comments = pick.comments.all() if pick else []
    
    is_member = False
    if request.user.is_authenticated:
        is_member = Membership.objects.filter(user=request.user, club=club).exists()
    
    members = club.members.all()
    
    return render(request, "clubs/club_detail.html", {
        "club": club,
        "pick": pick,
        "comments": comments,
        "is_member": is_member,
        "members": members,
    })
    
    
@login_required
def join_club(request, id):
    club = get_object_or_404(Club, id=id)
    
    if request.method == "POST":
        if not Membership.objects.filter(user=request.user, club=club).exists():
            Membership.objects.create(user=request.user, club=club)
    
    return redirect("club_detail", id=club.id)


@login_required
def leave_club(request, id):
    club = get_object_or_404(Club, id=id)
    
    if request.method == "POST":
        Membership.objects.filter(user=request.user, club=club).delete()
    
    return redirect("club_detail", id=club.id)
            

def nominations(request):
    pass

def create_nomination(request):
    pass
    
def close_pick(request):
    pass
    
    
    
        


            
