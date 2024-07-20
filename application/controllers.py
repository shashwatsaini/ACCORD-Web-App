from flask import Flask, Blueprint, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from datetime import datetime
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
    
status = {0: 'Pending', 1:'Rejected', 2:'Accepted', 3:'Completed, Pending Payment', 4:'Completed'}
request_state = {0: 'Pending', 1: 'Rejected', 2: 'Accepted'}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('userlogin.html', incorrect=False)
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        if Influencer.query.filter_by(username=username, password=password).first():
            user = Influencer.query.filter_by(username=username).first()
            login_user(load_user(username))
            return redirect(url_for('influencer_dashboard'))
        elif Sponsor.query.filter_by(username=username, password=password).first():
            user = Sponsor.query.filter_by(username=username).first()
            login_user(load_user(username))
            return redirect(url_for('sponsor_dashboard'))
        else:
            return render_template('userlogin.html', incorrect=True)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('adminlogin.html', incorrect=False)
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        if Admin.query.filter_by(username=username, password=password).first():
            user = Admin.query.filter_by(username=username).first()
            login_user(load_user(username))
            return redirect(url_for('admin-dashboard.html'))
        else:
            return render_template('adminlogin.html', incorrect=True)

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
            influencer = Influencer(username=username, name=name, bio=bio, password=password, platforms=platforms, category=category, niche=niche, reach=0, flag=0)
            db.session.add(influencer)
            db.session.commit()
            return redirect(url_for('login'))        

@app.route('/sponsor/register', methods=['GET', 'POST'])
def sponsor_registration():
    if request.method == 'GET':
        return render_template('sponsorregister.html', username_exists=False)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        company = request.form.get('company')
        bio = request.form.get('bio')
        industry = request.form.get('industry')

        if Influencer.query.filter_by(username=username).first():
            return render_template('sponsorregister.html', username_exists=True)
        elif Sponsor.query.filter_by(username=username).first():
            return render_template('sponsorregister.html', username_exists=True)
        else:
            sponsor = Sponsor(username=username, password=password, company=company, bio=bio, industry=industry, flag=0)
            db.session.add(sponsor)
            db.session.commit()
            return redirect(url_for('login'))

@app.route('/influencer/dashboard', methods=['GET', 'POST'])
#@login_required
def influencer_dashboard():
    if request.method == 'GET':
        ads_campaigns = (
            db.session.query(AdRequests, Campaign, Sponsor)
            .join(Campaign, AdRequests.campaign == Campaign.key)
            .join(Sponsor, Campaign.sponsor == Sponsor.username)
            .filter(AdRequests.influencer == 'influencer', AdRequests.status < 3)
            .all()[::-1]
        )
        sponsor_requests = (
            db.session.query(SponsorRequests, Campaign, Sponsor)
            .join(Campaign, SponsorRequests.campaign == Campaign.key)
            .join(Sponsor, SponsorRequests.sponsor == Sponsor.username)
            .filter(SponsorRequests.influencer == 'influencer', SponsorRequests.status == 0)
            .all()[::-1]
        )
        completed_requests = (
            db.session.query(AdRequests, Campaign, Sponsor)
            .join(Campaign, AdRequests.campaign == Campaign.key)
            .join(Sponsor, Campaign.sponsor == Sponsor.username)
            .filter(AdRequests.influencer == 'influencer', AdRequests.status >= 3)
            .all()[::-1]
        )
        past_sponsor_requests = (
            db.session.query(SponsorRequests, Campaign, Sponsor)
            .join(Campaign, SponsorRequests.campaign == Campaign.key)
            .join(Sponsor, SponsorRequests.sponsor == Sponsor.username)
            .filter(SponsorRequests.influencer == 'influencer', SponsorRequests.status == 1)
            .all()[::-1]
        )
        return render_template('influencerdashboard.html', ads_campaigns=ads_campaigns, completed_requests=completed_requests, sponsor_requests=sponsor_requests, past_sponsor_requests=past_sponsor_requests)

@app.route('/influencer/profile', methods=['GET'])
#@login_required
def influencer_profile():
    influencer = Influencer.query.get(current_user.username)
    ad_requests_completed = db.session.query(AdRequests).filter(AdRequests.influencer==current_user.username, AdRequests.status==4).count()
    return render_template('influencerprofile.html', influencer=influencer, ad_requests_completed=ad_requests_completed)

@app.route('/sponsor/find', methods=['GET','POST'])
#@login_required
def sponsor_find():
    return render_template('sponsorsearch.html')

@app.route('/influencer/ad-requests/mark-as-done/<int:key>', methods=['GET'])
#@login_required
def complete_ad_request(key):
    request = AdRequests.query.get(key)
    request.status = 3
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

@app.route('/influencer/sponsor-requests/accept/<int:key>', methods=['GET'])
#@login_required
def accept_sponsor_request(key):
    request = SponsorRequests.query.get(key)
    request.status = 2

    adrequest = AdRequests(influencer=request.influencer, sponsor=request.sponsor, campaign=request.campaign, description=request.description, niche=request.niche, payment=request.payment, status=2, flag=0)  
    db.session.add(adrequest)

    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

@app.route('/influencer/sponsor-requests/reject/<int:key>', methods=['GET'])
#@login_required
def reject_sponsor_request(key):
    request = SponsorRequests.query.get(key)
    request.status = 1
    db.session.commit()
    return redirect(url_for('influencer_dashboard'))

@app.route('/influencer/sponsor-requests/negotiate/<int:key>', methods=['GET', 'POST'])
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

@app.route('/sponsor/dashboard', methods=['GET', 'POST'])
#@login_required
def sponsor_dashboard():
    if request.method == 'GET':
        # Query campaigns
        campaigns = (
            db.session.query(Campaign)
            .filter(Campaign.sponsor == 'sponsor', Campaign.progress != 100)
            .order_by(Campaign.key.desc())
            .all()
        )
        ad_requests = (
            db.session.query(AdRequests)
            .filter(AdRequests.campaign.in_([campaign.key for campaign in campaigns]))  
            .all()
        )
        ad_requests_by_campaign = {}
        for ad_request in ad_requests:
            if ad_request.campaign not in ad_requests_by_campaign:
                ad_requests_by_campaign[ad_request.campaign] = []
            ad_requests_by_campaign[ad_request.campaign].append(ad_request)


        past_campaigns = (
            db.session.query(Campaign)
            .filter(Campaign.sponsor == 'sponsor', Campaign.progress == 100)
            .order_by(Campaign.key.desc())
            .all()
        )
        past_ad_requests = (
            db.session.query(AdRequests)
            .filter(AdRequests.campaign.in_([campaign.key for campaign in past_campaigns]))
            .all()
        )
        past_ad_requests_by_campaign = {}
        for ad_request in past_ad_requests:
            if ad_request.campaign not in past_ad_requests_by_campaign:
                past_ad_requests_by_campaign[ad_request.campaign] = []
            past_ad_requests_by_campaign[ad_request.campaign].append(ad_request)

        influencer_requests = (
            db.session.query(InfluencerRequests, Campaign, Influencer)
            .join(Campaign, InfluencerRequests.campaign == Campaign.key)
            .join(Influencer, InfluencerRequests.influencer == Influencer.username)
            .filter(InfluencerRequests.sponsor == 'sponsor', InfluencerRequests.status == 0)
            .all()[::-1]
        )
        past_influencer_requests = (
            db.session.query(InfluencerRequests, Campaign, Influencer)
            .join(Campaign, InfluencerRequests.campaign == Campaign.key)
            .join(Influencer, InfluencerRequests.influencer == Influencer.username)
            .filter(InfluencerRequests.sponsor == 'sponsor', InfluencerRequests.status != 0)
            .all()[::-1]
        )

        for campaign in campaigns:
            if campaign.end_date < datetime.now().date():
                campaign.progress = 100
                db.session.commit()
            else:
                campaign.progress = int((datetime.now().date() - campaign.start_date).days / (campaign.end_date - campaign.start_date).days * 100)
                db.session.commit()
        # Add logic to negotiation, view ad requests

        serialized_campaigns = []
        for campaign in campaigns:
            campaign_requests = ad_requests_by_campaign.get(campaign.key, [])
            serialized_campaigns.append({
                'name': campaign.name,
                'description': campaign.description,
                'progress': campaign.progress,
                'goals': campaign.goals,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'ad_requests': [request.to_dict() for request in campaign_requests]
            })
        
        serialized_past_campaigns = []
        for campaign in past_campaigns:
            campaign_requests = past_ad_requests_by_campaign.get(campaign.key, [])
            serialized_past_campaigns.append({
                'name': campaign.name,
                'description': campaign.description,
                'progress': campaign.progress,
                'goals': campaign.goals,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'ad_requests': [request.to_dict() for request in campaign_requests]
            })

        print(dir(influencer_requests[0]))

        return render_template('sponsordashboard.html', campaigns=serialized_campaigns, past_campaigns = serialized_past_campaigns, influencer_requests=influencer_requests, past_influencer_requests=past_influencer_requests)

@app.route('/sponsor/profile', methods=['GET'])
#@login_required
def sponsor_profile():
    sponsor = Sponsor.query.get(current_user.username)
    campaign_completed = db.session.query(Campaign).filter(Campaign.sponsor==current_user.username, Campaign.progress==100).count()
    ad_requests_completed = db.session.query(AdRequests).filter(AdRequests.sponsor==current_user.username, AdRequests.status==4).count()
    return render_template('sponsorprofile.html', sponsor=sponsor, campaign_completed=campaign_completed, ad_requests_completed=ad_requests_completed)

@app.route('/sponsor/create-campaign', methods=['GET', 'POST'])
#@login_required
def create_campaign():
    if request.method == 'GET':
        return render_template('createcampaign.html', company_name=current_user.company)
    else:
        name = request.form.get('campaign_name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        goals = request.form.get('goals')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        campaign = Campaign(sponsor=current_user.username, name=name, description=description, progress=0, start_date=start_date, end_date=end_date, budget=budget, goals=goals, flag=0)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/influencer-requests/accept/<int:key>', methods=['GET'])
#@login_required
def accept_influencer_request(key):
    request = InfluencerRequests.query.get(key)
    request.status = 2

    adrequest = AdRequests(influencer=request.influencer, sponsor=request.sponsor, campaign=request.campaign, description=request.description, niche=request.niche, payment=request.payment, status=2, flag=0)  
    db.session.add(adrequest)

    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/influencer-requests/reject/<int:key>', methods=['GET'])
#@login_required
def reject_influencer_request(key):
    request = InfluencerRequests.query.get(key)
    request.status = 1
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/influencer-requests/negotiate/<int:key>', methods=['GET', 'POST'])
def negotiate_influencer_request(key):
    if request.method == 'POST':
        payment = int(request.form.get('new_payment'))

        influencer_request = InfluencerRequests.query.get(key)
        influencer_request.payment = payment
        sponsor_request = SponsorRequests(influencer=influencer_request.influencer, sponsor=influencer_request.sponsor, campaign=influencer_request.campaign, description=influencer_request.description, niche=influencer_request.niche, payment=payment, status=0)
        db.session.add(sponsor_request)
        db.session.delete(influencer_request)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/payment/<int:key>', methods=['GET', 'POST'])
#@login_required
def payment(key):
    if request.method == 'GET':
        ad = (
            db.session.query(AdRequests, Influencer, Sponsor)
            .join(Influencer, AdRequests.influencer == Influencer.username)
            .join(Sponsor, AdRequests.sponsor == Sponsor.username)
            .filter(AdRequests.sponsor == 'sponsor', AdRequests.status != 4)
            .first()
        )
        return render_template('payment.html', influencer=(ad[1]).name, company=ad[2].company, amount=ad[0].payment, key=key)
    else:
        adrequest = AdRequests.query.get(key)
        adrequest.status = 4
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    