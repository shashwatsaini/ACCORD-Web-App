// Insights to be loaded automatically
document.addEventListener("DOMContentLoaded", function() {
    var username = document.getElementById('profileInsights').getAttribute('data-username');

    fetch(`/profile_insights?username=${encodeURIComponent(username)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('profileInsights').innerText = data.response;
    })
    .catch(error => console.error('Error:', error));
});

// Insights to be loaded after button clicks
function loadSponsorInsights(username) {

    fetch(`/profile_insights?username=${encodeURIComponent(username)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const elements = document.querySelectorAll(`[id^="profileInsights${username}"]`);
        elements.forEach(element => {
            element.innerText = data.response;
        });
    })
    .catch(error => console.error('Error:', error));
}

function loadInfluencerInsights(username) {

    fetch(`/profile_insights?username=${encodeURIComponent(username)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`profileInsights${username}`).innerText = data.response;
    })
    .catch(error => console.error('Error:', error));
}
