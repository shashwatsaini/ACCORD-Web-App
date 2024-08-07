from flask import Flask, request
from flask_login import login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from application.database import db
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign, InfluencerRequests, SponsorRequests

@login_manager.user_loader
def load_user(username):
    if Admin.query.get(username):
        return Admin.query.get(username)
    elif Influencer.query.get(username):
        return Influencer.query.get(username)
    elif Sponsor.query.get(username):
        return Sponsor.query.get(username)

# The page for influencer login
@app.route('/influencer/register', methods=['GET', 'POST'])
def influencer_registration():
    if request.method == 'GET':
        return render_template('influencerregister.html', username_exists=False)
    else:
        username = request.form.get('username')
        name = request.form.get('name')
        bio = request.form.get('bio')
        password = request.form.get('password')
        platforms = request.form.get('selectedPlatforms')
        category = request.form.get('category')
        niche = request.form.get('niche')

        if Influencer.query.filter_by(username=username).first():
            return render_template('influencerregister.html', username_exists=True)
        elif Sponsor.query.filter_by(username=username).first():
            return render_template('influencerregister.html', username_exists=True)
        else:
            influencer = Influencer(username=username, name=name, bio=bio, password=password, platforms=platforms, category=category, niche=niche, flag=0)
            db.session.add(influencer)
            db.session.commit()
            return redirect(url_for('login'))   

# The page for influencer dashboard
@app.route('/influencer/dashboard', methods=['GET', 'POST'])
@login_required
def influencer_dashboard():
    if request.method == 'GET':
        ads_campaigns = (
            db.session.query(AdRequests, Campaign, Sponsor)
            .join(Campaign, AdRequests.campaign == Campaign.key)
            .join(Sponsor, Campaign.sponsor == Sponsor.username)
            .filter(AdRequests.influencer == current_user.username, AdRequests.status <= 3)
            .all()[::-1]
        )
        sponsor_requests = (
            db.session.query(SponsorRequests, Campaign, Sponsor)
            .join(Campaign, SponsorRequests.campaign == Campaign.key)
            .join(Sponsor, SponsorRequests.sponsor == Sponsor.username)
            .filter(SponsorRequests.influencer == current_user.username, SponsorRequests.status == 0)
            .all()[::-1]
        )
        completed_requests = (
            db.session.query(AdRequests, Campaign, Sponsor)
            .join(Campaign, AdRequests.campaign == Campaign.key)
            .join(Sponsor, Campaign.sponsor == Sponsor.username)
            .filter(AdRequests.influencer == current_user.username, AdRequests.status >= 3)
            .all()[::-1]
        )
        past_sponsor_requests = (
            db.session.query(SponsorRequests, Campaign, Sponsor)
            .join(Campaign, SponsorRequests.campaign == Campaign.key)
            .join(Sponsor, SponsorRequests.sponsor == Sponsor.username)
            .filter(SponsorRequests.influencer == current_user.username, SponsorRequests.status == 1)
            .all()[::-1]
        )
        return render_template('influencerdashboard.html', ads_campaigns=ads_campaigns, completed_requests=completed_requests, sponsor_requests=sponsor_requests, past_sponsor_requests=past_sponsor_requests)

# The page for influencer profile
@app.route('/influencer/profile', methods=['GET'])
@login_required
def influencer_profile():
    influencer = Influencer.query.get(current_user.username)
    ad_requests_completed = db.session.query(AdRequests).filter(AdRequests.influencer==current_user.username, AdRequests.status==4).count()
    return render_template('influencerprofile.html', influencer=influencer, ad_requests_completed=ad_requests_completed)

# The page for influencer to find campaigns
@app.route('/influencer/find', methods=['GET','POST'])
@login_required
def campaign_find():
    if request.method == 'GET':
        if request.args.get('niche'):
            niche = request.args.get('niche')
            campaign_count = db.session.query(db.func.count(Campaign.key)).filter(Campaign.progress == 100).label('campaign_count')
            adrequest_count = db.session.query(db.func.count(AdRequests.key)).filter(AdRequests.status == 4).label('adrequest_count')
            campaigns = (
                db.session.query(Campaign, Sponsor, campaign_count, adrequest_count)
                .filter(Campaign.niche == niche, Campaign.progress != 100, Campaign.sponsor == Sponsor.username, Campaign.flag == 0)
                .all()
            )
            return render_template('campaignsearch.html', campaigns=campaigns)
        else:
            campaign_count = db.session.query(db.func.count(Campaign.key)).filter(Campaign.progress == 100).label('campaign_count')
            adrequest_count = db.session.query(db.func.count(AdRequests.key)).filter(AdRequests.status == 4).label('adrequest_count')
            campaigns = (
                db.session.query(Campaign, Sponsor, campaign_count, adrequest_count)
                .filter(Campaign.progress != 100, Campaign.sponsor == Sponsor.username, Campaign.flag == 0)
                .all()
            )
            return render_template('campaignsearch.html', campaigns=campaigns)

# The endpoint for influencer to create a request to join a campaign
@app.route('/influencer/sponsor-requests/create', methods=['POST'])
@login_required
def create_influencer_request():
    if request.method == 'POST':
        sponsor = request.form.get('sponsor-username')
        campaign = request.form.get('campaign')
        description = request.form.get('description')
        niche = request.form.get('niche')
        payment = request.form.get('payment')

        influencer_request = InfluencerRequests(influencer=current_user.username, sponsor=sponsor, campaign=campaign, description=description, niche=niche, payment=payment, status=0)
        db.session.add(influencer_request)
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))

# The endpoint for influencer to mark an ad request as completed
@app.route('/influencer/ad-requests/mark-as-done/<int:key>', methods=['GET'])
@login_required
def complete_ad_request(key):
    request = AdRequests.query.get(key)
    request.status = 3
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

# The endpoint for influencer to accept a sponsor request
@app.route('/influencer/sponsor-requests/accept/<int:key>', methods=['GET'])
@login_required
def accept_sponsor_request(key):
    request = SponsorRequests.query.get(key)
    request.status = 2

    adrequest = AdRequests(influencer=request.influencer, sponsor=request.sponsor, campaign=request.campaign, description=request.description, niche=request.niche, payment=request.payment, status=2, flag=0)  
    db.session.add(adrequest)

    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

# The endpoint for influencer to reject a sponsor request
@app.route('/influencer/sponsor-requests/reject/<int:key>', methods=['GET'])
@login_required
def reject_sponsor_request(key):
    request = SponsorRequests.query.get(key)
    request.status = 1
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

# The endpoint for influencer to negotiate a sponsor request
@app.route('/influencer/sponsor-requests/negotiate/<int:key>', methods=['POST'])
def negotiate_sponsor_request(key):
    if request.method == 'POST':
        payment = int(request.form.get('new_payment'))

        sponsor_request = SponsorRequests.query.get(key)
        sponsor_request.payment = payment
        influencer_request = InfluencerRequests(influencer=sponsor_request.influencer, sponsor=sponsor_request.sponsor, campaign=sponsor_request.campaign, description=sponsor_request.description, niche=sponsor_request.niche, payment=payment, status=0)
        db.session.add(influencer_request)
        db.session.delete(sponsor_request)
        db.session.commit()
        return redirect(url_for('influencer_dashboard'))
    