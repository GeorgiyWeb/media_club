# Media Club

A Django web application for creating and managing interest clubs around
books, movies, music, or games. Each club has a current "pick" — the item
members are discussing right now. Members can comment on the current pick,
suggest nominations for the next one, and vote for their favorite. When the
club owner closes the current pick, the most voted nomination automatically
becomes the new active pick.

## Distinctiveness and Complexity

This project is sufficiently distinct from the other CS50W assignments and
is more complex than them.

First, it is not a social network. While it has users, profiles, and
comments, the core of the application is not about connecting people or
building a feed. There is no "following" system, no timeline of posts, and
no private messaging. The central mechanic is a **content discussion
pipeline**: a club always has exactly one active pick, members nominate
candidates for the next pick, they vote, and when the owner closes the
current pick, the winner automatically becomes the next one. This pipeline
is unique to this project and does not exist in Project 4 (Network).

Second, it is not an e-commerce site. There is no buying, selling,
auctioning, or bidding. There are no products, prices, or orders. The
project is entirely about collaborative content selection and discussion.

Third, the project is more complex than previous assignments. It uses six
interconnected models (Club, Membership, Pick, Comment, Nomination, Vote)
with several ForeignKey and ManyToMany relationships, including a
ManyToManyField through a custom intermediate model (Membership) and a
unique_together constraint on votes. It implements a non-trivial state
transition (closing a pick and promoting the winner) that involves
updating, creating, and deleting multiple objects in a specific order.
It also uses JavaScript with the fetch API to update vote counts
dynamically without reloading the page, and handles CSRF protection for
asynchronous requests.

Finally, the application is mobile-responsive thanks to Bootstrap's grid
system and utility classes. Forms, cards, and the navigation bar all adapt
to different screen sizes.

## Features

- User registration, login, and logout
- Create clubs with a name, description, and category (Books, Movies, Music, Games)
- The creator automatically becomes a member and sets the first pick
- Join and leave clubs
- Comment on the current pick
- Suggest nominations for the next pick
- Vote for nominations (toggle: click to vote, click again to remove the vote)
- Close the current pick — the most voted nomination becomes the new pick, and remaining votes are reset
- View user profiles with memberships, created clubs, and nomination count
- Filter clubs by category on the home page

## Files

- `clubs/models.py` — Defines six models: Club (name, description, category, creator, members), Membership (user-club link with date, unique per pair), Pick (title, creator, club, author, is_active flag), Comment (text, author, pick, date), Nomination (title, creator, club, author, date), Vote (nomination, user, date, unique per pair).

- `clubs/views.py` — Contains all views: `index` (list clubs with optional category filter), `profile` (user profile), `register` (user creation with auto-login), `club_create` (form + first pick + membership), `club_detail` (club page with pick, comments, members), `join_club`, `leave_club`, `create_comment`, `nominations`, `create_nomination`, `vote` (JSON response), `close_pick` (promotes the winning nomination).

- `clubs/urls.py` — URL routes for the clubs app, including auth routes (login, logout) and all project-specific endpoints.

- `clubs/forms.py` — Contains `ClubCreateForm`, a ModelForm for Club with two extra fields for the first pick (title and creator).

- `clubs/admin.py` — Registers all models in the Django admin with list displays and filters.

- `clubs/templates/clubs/` — HTML templates: `layout.html` (base template with navbar and Bootstrap), `index.html` (club list + filter), `club_detail.html` (club page), `nominations.html` (nomination list + voting), `club_create.html`, `profile.html`, `register.html`.

- `clubs/templates/registration/login.html` — Login page.

- `clubs/static/vote.js` — JavaScript that handles asynchronous voting via the fetch API: listens for clicks on `.vote-btn`, sends a POST request to `/clubs/vote/<id>/`, updates the vote counter and button appearance without reloading the page.

- `clubs/static/styles/style.css` — Custom CSS for form layout, help text, and error styling.

- `mediaclub/settings.py` — Django project settings.

- `mediaclub/urls.py` — Root URL configuration that includes the clubs app and admin.

- `requirements.txt` — Python dependencies (Django 6.1).

## How to Run

1. Install Django:
   ```
   pip install -r requirements.txt
   ```

2. Apply migrations:
   ```
   python manage.py migrate
   ```

3. Run the development server:
   ```
   python manage.py runserver
   ```

4. Open http://127.0.0.1:8000/ in your browser.

## Technologies

- Django 6.1 (backend, models, views, forms, auth)
- Bootstrap 5 (responsive layout, cards, buttons, navbar via CDN)
- Vanilla JavaScript (fetch API for voting, DOM manipulation)
- SQLite (database)

## Sources

- Django documentation: https://docs.djangoproject.com/
- Bootstrap 5 documentation: https://getbootstrap.com/docs/5.3/
- MDN Web Docs for JavaScript: fetch, DOMContentLoaded, classList, addEventListener
- CS50W lecture notes and sections

## Additional Information

This project was built as the final Capstone for CS50W. It uses Django's
built-in authentication system (`django.contrib.auth`) for user management.
The voting system prevents duplicate votes via a `unique_together`
constraint on the Vote model. The "close pick" feature is restricted to
the club creator and implements a specific winner-selection algorithm:
nominations are compared by vote count, and the one with the most votes
becomes the next pick. If there are no nominations or no active pick, the
action is safely ignored.