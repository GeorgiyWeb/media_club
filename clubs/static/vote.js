document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.vote-btn');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            const id = button.dataset.nominationId;
            const token = getToken('csrftoken');

            fetch('/clubs/vote/' + id + '/', {
                method: 'POST',
                headers: { 'X-CSRFToken': token },
            })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                const card = button.closest('.nomination');
                const counter = card.querySelector('.vote-count');
                counter.textContent = data.votes;

                if (data.voted) {
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-primary');
                } else {
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-outline-primary');
                }
            });
        });

    });
});



function getToken(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const c = cookies[i].trim();
        if (c.indexOf(name + '=') === 0) {
            return c.substring(name.length + 1);
        }
    }
    return null;

}

// References:
// - DOMContentLoaded, querySelectorAll, addEventListener — MDN Web Docs
// - fetch API and Promises — MDN Web Docs
// - classList.toggle/remove/add — MDN Web Docs
// - Reading CSRF token from cookies — Django documentation
