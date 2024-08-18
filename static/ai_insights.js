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

// Sponsor Insights
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

// Influencer Insights
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

// Campaign Insights
function loadCampaignInsights(key) {

    fetch(`/campaign_insights?key=${encodeURIComponent(key)}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`campaignInsights${key}`).innerText = data.response;
    })
    .catch(error => console.error('Error:', error));
}
