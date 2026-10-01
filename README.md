# Media Club

Media Club is a Django web application for creating and running interest clubs built around books, movies, music, or games. Every club revolves around one shared piece of media, called the **current pick**. Members read, watch, or play it together and discuss it in comments. While they do, they propose **nominations** for what the club should enjoy next and **vote** on them. When the club owner decides the group is done with the current pick, the nomination with the most votes automatically becomes the new pick, and the cycle starts again.

## Distinctiveness and Complexity

### What the project is

Media Club is a **collaborative content-curation and discussion platform**. Its central idea is a repeating three-stage cycle that every club goes through:

1. **Discuss** – members comment on the club's single active pick.
2. **Nominate** – members propose candidates for the next pick.
3. **Vote** – members vote for their favorite nomination; the vote can be toggled on and off.

The cycle ends when the owner closes the current pick. At that moment the application promotes the winning nomination to the new active pick, archives the previous pick (it stays in the database with `is_active` set to `False`), and resets all votes on the remaining nominations so the next round starts fresh. Nominations that did not win stay on the list and can compete again. The club therefore has one active pick at a time, and what it discusses next is decided democratically by its members.

This makes the application a small **workflow engine** with rules about who may do what and when. Logged-in users can join clubs, comment, nominate, and vote. Only the creator can close a pick. A user can vote only once per nomination, and the application promotes exactly one active pick per club at a time. Users do not just post content into a feed. They take part in a shared decision-making process whose outcome (the next pick) is computed by the server, and the whole club's attention is focused on that outcome. The interesting data (what the club is reading right now, what it is considering next, and how popular each candidate is) is the product of the application's own logic rather than of free-form user posts.

Around this core, the application provides the supporting features a real community needs: registration and authentication, category-based browsing (Books, Movies, Music, Games), join/leave membership, and user profiles showing a person's memberships, the clubs they created, and how many nominations they have made.

### Why it is complex

**Data model.** The project uses six interconnected models: `Club`, `Membership`, `Pick`, `Comment`, `Nomination`, and `Vote`. `Club` and `User` are related through a `ManyToManyField` that goes through the custom intermediate model `Membership`, which stores the join date and enforces one membership per user-club pair. Picks, comments, nominations, and votes are linked through chains of `ForeignKey` relationships (for example, `Vote → Nomination → Club` and `Comment → Pick → Club`). The model layer also relies on database-level integrity: `unique_together` on `Membership` and on `Vote` guarantee at the database level that a user cannot have duplicate memberships or duplicate votes.

**Non-trivial state transition.** Closing a pick is the most complex operation in the project. The `close_pick` view must (a) verify that the request is a POST from the club's creator, (b) find the currently active pick, (c) count the votes of every nomination in the club and select the one with the most, (d) deactivate the old pick, (e) create a new active pick from the winner's title, creator, and author, (f) delete the winning nomination (which cascades to its votes), and (g) delete all votes on the remaining nominations so the next round starts from zero. These steps update, create, and delete several kinds of objects in a specific order. The view also handles edge cases safely: a request from a non-owner is redirected, and a club with no nominations or no active pick is left unchanged rather than causing errors or corrupting data.

**Asynchronous front end.** Voting is implemented with JavaScript and the `fetch` API instead of full page reloads. When a user clicks a vote button, `vote.js` sends a `POST` request to a JSON endpoint, reads the server's response, and updates both the vote counter and the button's appearance in the DOM. Because the request is made from JavaScript, the script must read the CSRF token and send it in the request headers so that Django's CSRF protection stays active. The server-side view toggles the vote (it creates the `Vote` if none exists and deletes it if it does) and returns the new count as JSON.

**Access control and authorization.** The application distinguishes between anonymous visitors (who can browse clubs, profiles, and nominations), logged-in users, and club owners. Views that change data are protected with Django's `@login_required` and act only on POST requests, and the owner-only close-pick action is checked on the server (`club.creator != request.user`) rather than only hidden in the template.

**Responsive design.** The interface is built with Bootstrap 5's grid and utility classes, so the club cards (a `col-md-4` grid) and the nomination form (columns that stack) reflow on small screens, and the base template sets the viewport meta tag for mobile devices.

## Features

- User registration (with automatic login), login, and logout
- Create clubs with a name, description, and category (Books, Movies, Music, Games)
- The creator automatically becomes a member and sets the club's first pick
- Join and leave clubs
- Comment on the current pick
- Suggest nominations for the next pick
- Vote for nominations (click to vote, click again to remove the vote), updated live without a page reload
- Close the current pick: the most voted nomination becomes the new pick and remaining votes are reset (owner only)
- View user profiles with memberships, created clubs, and nomination count
- Filter clubs by category on the home page
- Manage all data through the Django admin

## Files and Directories

### Project root

- `manage.py` – Django's standard command-line utility, used to run the server and apply migrations.
- `requirements.txt` – Python dependencies (Django 6.1).
- `README.md` – this document.
- `.gitignore` – lists files that should not be tracked by Git (Python caches, the local database, and similar).
- `db.sqlite3` – the SQLite database. It is created locally by `python manage.py migrate` and is not part of the repository.

### `mediaclub/` (project configuration)

- `__init__.py` – marks the directory as a Python package.
- `asgi.py` / `wsgi.py` – entry points for ASGI and WSGI servers, generated by Django.
- `settings.py` – Django project settings: installed apps (including `clubs`), database configuration (SQLite), static files, authentication redirect URLs, and middleware (including CSRF protection).
- `urls.py` – root URL configuration. It includes the `clubs` app's URLs and the Django admin.

### `clubs/` (main application)

- `__init__.py` – marks the directory as a Python package.
- `apps.py` – application configuration (`ClubsConfig`), generated by Django.
- `tests.py` – Django's default test module for the app.
- `models.py` – defines the six models:
  - `Club` – name, description, category (Books/Movies/Music/Games), creator, and a many-to-many `members` field through `Membership`.
  - `Membership` – links a user to a club and stores the join date; unique per user-club pair.
  - `Pick` – the media item a club is currently discussing (`title`; `creator`, the name of the book's author, film's director, or artist; the `club`; `author`, the user who added it; an `is_active` flag; and a `begin_date`).
  - `Comment` – text, author, the pick it belongs to, and the publication date; comments are ordered newest first.
  - `Nomination` – a candidate for the next pick (`title`, `creator` as the name of the media's creator, the `club`, `author` as the user who nominated it, and a `date`).
  - `Vote` – links a user to a nomination with a date; unique per user-nomination pair, which prevents duplicate votes.
- `views.py` – contains all of the application's logic:
  - `index` – lists clubs and supports filtering by category.
  - `profile` – shows a user's memberships, created clubs, and nomination count.
  - `register` – creates a user and logs them in automatically.
  - `club_create` – handles the club form, creates the first pick, and adds the creator as a member.
  - `club_detail` – shows a club's current pick, comments, and members.
  - `join_club` / `leave_club` – create or remove a membership.
  - `create_comment` – saves a comment on the current pick.
  - `nominations` – lists a club's nominations and collects the ids of the nominations the current user has already voted for, so the page shows the correct vote state after a reload.
  - `create_nomination` – saves a new nomination.
  - `vote` – toggles a vote and returns the result as JSON for `vote.js`.
  - `close_pick` – owner-only; deactivates the current pick, creates a new pick from the most voted nomination, deletes that nomination, and resets the votes on the others.
- `urls.py` – URL routes for the app, including the login and logout routes and every endpoint above.
- `forms.py` – contains `ClubCreateForm`, a `ModelForm` for `Club` (fields: name, description, category) extended with two extra fields, `pick_title` ("What are we discussing first?") and `pick_creator` ("Who is the author?"). This lets a club and its first pick be created in one form; `club_create` in `views.py` reads these two values and builds the `Pick`.
- `admin.py` – registers all six models in the Django admin with custom list displays and filters.
- `migrations/` – database migrations generated from the models.

### `clubs/templates/clubs/`

- `layout.html` – base template with the Bootstrap 5 CDN links, navbar (a Create Club button, profile link, and a POST-based Logout form for logged-in users; Log In and Register links for visitors), and the blocks the other templates extend.
- `index.html` – home page with the list of clubs as cards and the category filter.
- `club_detail.html` – a single club's page: current pick, comment list and form, member list, and join/leave and close-pick buttons depending on the viewer's role.
- `nominations.html` – the list of nominations with vote counts and vote buttons (highlighted for nominations the user has already voted for), plus the form to add a nomination.
- `club_create.html` – the form for creating a club and its first pick.
- `profile.html` – a user's profile page.
- `register.html` – the registration form.

### `clubs/templates/registration/`

- `login.html` – the login page used by Django's built-in authentication views.

### `clubs/static/`

- `vote.js` – handles asynchronous voting. It listens for clicks on `.vote-btn` elements, sends a `POST` request to `/clubs/vote/<id>/` using `fetch` (the CSRF token is read from the `csrftoken` cookie by a helper function and sent in the `X-CSRFToken` header), and updates the vote counter and button style from the JSON response without reloading the page.
- `styles/style.css` – custom CSS for form layout, help text, and error message styling, complementing Bootstrap.

## How to Run

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Apply the migrations:

   ```
   python manage.py migrate
   ```

3. (Optional) Create an admin user:

   ```
   python manage.py createsuperuser
   ```

4. Start the development server:

   ```
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/ in your browser.

## Technologies

- Django 6.1 (models, views, forms, authentication)
- Bootstrap 5 via CDN (responsive layout, cards, buttons, navbar)
- Vanilla JavaScript (fetch API, DOM manipulation)
- SQLite

## Additional Information

The project uses Django's built-in authentication system (`django.contrib.auth`). Duplicate votes are prevented by a `unique_together` constraint on `Vote`, and duplicate memberships by the same kind of constraint on `Membership`. The close-pick action is restricted to the club creator and chooses the winner by comparing vote counts across the club's nominations. If there are no nominations or no active pick, the action is safely ignored.

## Sources

- Django documentation: https://docs.djangoproject.com/
- Bootstrap 5 documentation: https://getbootstrap.com/docs/5.3/
- MDN Web Docs (fetch, DOMContentLoaded, classList, addEventListener)
- CS50W lecture notes and sections
