from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Club, Nomination, Pick, Membership, Comment, Vote
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
            

@login_required
def vote(request, nomination_id):
    nomination = get_object_or_404(Nomination, id=nomination_id)
    
    if request.method == "POST":
        vote_obj = Vote.objects.filter(nomination=nomination, user=request.user).first()
        
        if vote_obj:
            vote_obj.delete()
            voted = False
            
        else:
            Vote.objects.create(nomination=nomination, user=request.user)
            voted = True
            
        return JsonResponse({"votes" : nomination.votes.count(), "voted" : voted,})
    
    return JsonResponse({"error" : "POST required"}, status=400)
        

@login_required
def create_comment(request, pick_id):
    pick = get_object_or_404(Pick, pk=pick_id)
    
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(pick=pick, author=request.user, text=text)
    
    return redirect("club_detail", id=pick.club.id)
    

def club_detail(request, id):
    club = get_object_or_404(Club, pk=id)
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
    club = get_object_or_404(Club, pk=id)
    
    if request.method == "POST":
        if not Membership.objects.filter(user=request.user, club=club).exists():
            Membership.objects.create(user=request.user, club=club)
    
    return redirect("club_detail", id=club.id)


@login_required
def leave_club(request, id):
    club = get_object_or_404(Club, pk=id)
    
    if request.method == "POST":
        Membership.objects.filter(user=request.user, club=club).delete()
    
    return redirect("club_detail", id=club.id)
            

def nominations(request, id):
    club = get_object_or_404(Club, pk=id)
    nomination_list = Nomination.objects.filter(club=club)
    is_member = False
    
    if request.user.is_authenticated:
        is_member = Membership.objects.filter(user=request.user, club=club).exists()
        
    return render(request, "clubs/nominations.html", {'club' : club,
                                                      'nomination_list' : nomination_list,
                                                      "is_member" : is_member})


@login_required
def create_nomination(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if request.method == "POST":
        title = request.POST.get("title")
        creator = request.POST.get("creator")
        
    if title and creator:
        Nomination.objects.create(club=club,
                                  author=request.user,
                                  title=title,
                                  creator=creator)
    
    return redirect("nomination_list", id=club.id)
    
    
@login_required
def close_pick(request, id):
    club = get_object_or_404(Club, id=id)
    
    if club.creator != request.user:
        return redirect("club_detail", id=club.id)
    
    if request.method == "POST":
        current_pick = club.picks.filter(is_active=True).first()
        
        nominations = club.nominations.all()
        winner = max(nominations, key=lambda n: n.votes.count(), default=None)
        
        if current_pick and winner:
            current_pick.is_active = False
            current_pick.save()
            
            Pick.objects.create(
                title=winner.title,
                creator=winner.creator,
                club=club,
                author=winner.author,
                is_active=True,
            )
            
            winner.delete()
            
            for nomination in club.nominations.all():
                nomination.votes.all().delete()
    
    return redirect("club_detail", id=club.id)
    
    
    
    
        


            
          
