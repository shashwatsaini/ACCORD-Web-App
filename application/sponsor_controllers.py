from flask import Flask, request
from flask_login import login_user, login_required, logout_user, current_user
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

# The page for a sponsor to register
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

# The page for a sponsor to view their dashboard
@app.route('/sponsor/dashboard', methods=['GET', 'POST'])
@login_required
def sponsor_dashboard():
    if request.method == 'GET':
        # campaigns and past_campaigns query require a join for all ad requests to its each campaign
        # This is then converted into a json by serializing the data
        campaigns = (
            db.session.query(Campaign)
            .filter(Campaign.sponsor == current_user.username   , Campaign.progress != 100)
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
            .filter(Campaign.sponsor == current_user.username, Campaign.progress == 100)
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

        adrequest_subquery = (
        db.session.query(
                AdRequests.influencer.label('influencer'),
                db.func.count(AdRequests.status).filter(AdRequests.status == 4).label('adrequest_count'),
            )
            .group_by(AdRequests.influencer)
            .subquery()
        )
        influencer_requests = (
            db.session.query(
                InfluencerRequests,
                Campaign,
                Influencer,
                adrequest_subquery.c.adrequest_count
            )
            .join(Campaign, InfluencerRequests.campaign == Campaign.key)
            .join(Influencer, InfluencerRequests.influencer == Influencer.username)
            .outerjoin(adrequest_subquery, InfluencerRequests.influencer == adrequest_subquery.c.influencer)
            .filter(InfluencerRequests.sponsor == current_user.username, InfluencerRequests.status == 0)
            .all()[::-1]
        )
        past_influencer_requests = (
            db.session.query(InfluencerRequests, Campaign, Influencer)
            .join(Campaign, InfluencerRequests.campaign == Campaign.key)
            .join(Influencer, InfluencerRequests.influencer == Influencer.username)
            .filter(InfluencerRequests.sponsor == current_user.username, InfluencerRequests.status != 0)
            .all()[::-1]
        )

        # Updating progress of campaigns based on current date
        for campaign in campaigns:
            if campaign.end_date < datetime.now().date():
                campaign.progress = 100
                db.session.commit()
            else:
                campaign.progress = int((datetime.now().date() - campaign.start_date).days / (campaign.end_date - campaign.start_date).days * 100)
                db.session.commit()

        serialized_campaigns = []
        for campaign in campaigns:
            campaign_requests = ad_requests_by_campaign.get(campaign.key, [])
            serialized_campaigns.append({
                'key': campaign.key,
                'name': campaign.name,
                'description': campaign.description,
                'niche': campaign.niche,
                'progress': campaign.progress,
                'goals': campaign.goals,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'flag': campaign.flag,
                'ad_requests': [request.to_dict() for request in campaign_requests]
            })
        
        serialized_past_campaigns = []
        for campaign in past_campaigns:
            campaign_requests = past_ad_requests_by_campaign.get(campaign.key, [])
            serialized_past_campaigns.append({
                'name': campaign.name,
                'description': campaign.description,
                'niche': campaign.niche,
                'progress': campaign.progress,
                'goals': campaign.goals,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'ad_requests': [request.to_dict() for request in campaign_requests]
            })

        return render_template('sponsordashboard.html', campaigns=serialized_campaigns, past_campaigns = serialized_past_campaigns, influencer_requests=influencer_requests, past_influencer_requests=past_influencer_requests)

# The page for a sponsor to find influencers
@app.route('/sponsor/find', methods=['GET','POST'])
@login_required
def sponsor_find():
    if request.method == 'GET':
        if request.args.get('category') and request.args.get('niche'):
            category = request.args.get('category')
            niche = request.args.get('niche')
             # Gets ad requests completed for each influencer
            adrequest_subquery = (
                db.session.query(
                        AdRequests.influencer.label('influencer'),
                        db.func.count(AdRequests.status).filter(AdRequests.status == 4).label('adrequests_count')
                    )
                    .group_by(AdRequests.influencer)
                    .subquery()
            )
            influencers = (
                db.session.query(
                    Influencer,
                    adrequest_subquery.c.adrequests_count
                )
                .filter(Influencer.category == category, Influencer.niche == niche, Influencer.flag == 0)
                .outerjoin(adrequest_subquery, Influencer.username == adrequest_subquery.c.influencer)
                .all()
            )
        elif request.args.get('category'):
            category = request.args.get('category')
             # Gets ad requests completed for each influencer
            adrequest_subquery = (
                db.session.query(
                        AdRequests.influencer.label('influencer'),
                        db.func.count(AdRequests.status).filter(AdRequests.status == 4).label('adrequests_count')
                    )
                    .group_by(AdRequests.influencer)
                    .subquery()
            )
            influencers = (
                db.session.query(
                    Influencer,
                    adrequest_subquery.c.adrequests_count
                )
                .filter(Influencer.category == category, Influencer.flag == 0)
                .outerjoin(adrequest_subquery, Influencer.username == adrequest_subquery.c.influencer)
                .all()
            )
        elif request.args.get('niche'):
            niche = request.args.get('niche')
             # Gets ad requests completed for each influencer
            adrequest_subquery = (
                db.session.query(
                        AdRequests.influencer.label('influencer'),
                        db.func.count(AdRequests.status).filter(AdRequests.status == 4).label('adrequests_count')
                    )
                    .group_by(AdRequests.influencer)
                    .subquery()
            )
            influencers = (
                db.session.query(
                    Influencer,
                    adrequest_subquery.c.adrequests_count
                )
                .filter(Influencer.niche == niche, Influencer.flag == 0)
                .outerjoin(adrequest_subquery, Influencer.username == adrequest_subquery.c.influencer)
                .all()
            )
        else:
            # Gets ad requests completed for each influencer
            adrequest_subquery = (
                db.session.query(
                        AdRequests.influencer.label('influencer'),
                        db.func.count(AdRequests.status).filter(AdRequests.status == 4).label('adrequests_count')
                    )
                    .group_by(AdRequests.influencer)
                    .subquery()
            )
            influencers = (
                db.session.query(
                    Influencer,
                    adrequest_subquery.c.adrequests_count
                )
                .outerjoin(adrequest_subquery, Influencer.username == adrequest_subquery.c.influencer)
                .filter(Influencer.flag == 0)
                .all()
            )
        campaigns = Campaign.query.filter(Campaign.sponsor == current_user.username).all()
        return render_template('sponsorsearch.html', influencers=influencers, campaigns=campaigns)
    return render_template('sponsorsearch.html')

# The page for a sponsor to view their profile
@app.route('/sponsor/profile', methods=['GET'])
@login_required
def sponsor_profile():
    sponsor = Sponsor.query.get(current_user.username)
    campaign_completed = db.session.query(Campaign).filter(Campaign.sponsor==current_user.username, Campaign.progress==100).count()
    ad_requests_completed = db.session.query(AdRequests).filter(AdRequests.sponsor==current_user.username, AdRequests.status==4).count()
    return render_template('sponsorprofile.html', sponsor=sponsor, campaign_completed=campaign_completed, ad_requests_completed=ad_requests_completed)

# The page for a sponsor to create a campaign 
@app.route('/sponsor/create-campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'GET':
        return render_template('createcampaign.html', company_name=current_user.company)
    else:
        name = request.form.get('campaign_name')
        description = request.form.get('description')
        niche = request.form.get('niche')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        goals = request.form.get('goals')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        campaign = Campaign(sponsor=current_user.username, name=name, description=description, niche=niche, progress=0, start_date=start_date, end_date=end_date, budget=budget, goals=goals, flag=0)
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

# The page for a sponsor to modify a campaign
@app.route('/sponsor/modify-campaign/<int:key>', methods=['GET', 'POST'])
@login_required
def modify_campaign(key):
    if request.method == 'GET':
        campaign = Campaign.query.get(key)
        return render_template('modifycampaign.html', company_name=current_user.company, campaign=campaign)
    else:
        name = request.form.get('campaign_name')
        description = request.form.get('description')
        niche = request.form.get('niche')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        goals = request.form.get('goals')

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        campaign = Campaign.query.get(key)
        campaign.name = name
        campaign.description = description
        campaign.niche = niche
        campaign.start_date = start_date
        campaign.end_date = end_date
        campaign.budget = budget
        campaign.goals = goals
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

# The enddpoint for a sponsor to delete a campaign
@app.route('/sponsor/delete-campaign/<int:key>', methods=['GET'])
@login_required
def delete_campaign(key):
    campaign = Campaign.query.get(key)

    adrequests = AdRequests.query.filter(AdRequests.campaign == key).all()
    for adrequest in adrequests:
        db.session.delete(adrequest)

    infuencer_requests = InfluencerRequests.query.filter(InfluencerRequests.campaign == key).all()
    for influencer_request in infuencer_requests:
        db.session.delete(influencer_request)
    
    sponsor_requests = SponsorRequests.query.filter(SponsorRequests.campaign == key).all()
    for sponsor_request in sponsor_requests:
        db.session.delete(sponsor_request)

    db.session.delete(campaign)
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

# The endpoint for a sponsor to create an ad request
@app.route('/sponsor/ad-requests/modify/<int:key>', methods=['POST'])
@login_required
def modify_ad_request(key):
    if request.method == 'POST':
        description = request.form.get('description')
        niche = request.form.get('niche')
        payment = request.form.get('payment')
        ad_request = AdRequests.query.get(key)
        ad_request.description = description
        ad_request.niche = niche
        ad_request.payment = payment
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

# The endpoint for a sponsor to send a request to an influencer
@app.route('/sponsor/influencer-requests/create', methods=['GET', 'POST'])
@login_required
def create_sponsor_request():
    if request.method == 'POST':
        influencer = request.form.get('influencer-username')
        campaign = request.form.get('campaign')
        description = request.form.get('description')
        niche = request.form.get('niche')
        payment = request.form.get('payment')

        sponsor_request = SponsorRequests(influencer=influencer, sponsor=current_user.username, campaign=campaign, description=description, niche=niche, payment=payment, status=0)
        db.session.add(sponsor_request)
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))

# The endpoint for a sponsor to accept an influencer request
@app.route('/sponsor/influencer-requests/accept/<int:key>', methods=['GET'])
@login_required
def accept_influencer_request(key):
    request = InfluencerRequests.query.get(key)
    request.status = 2

    adrequest = AdRequests(influencer=request.influencer, sponsor=request.sponsor, campaign=request.campaign, description=request.description, niche=request.niche, payment=request.payment, status=2, flag=0)  
    db.session.add(adrequest)

    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

# The endpoint for a sponsor to reject an influencer request
@app.route('/sponsor/influencer-requests/reject/<int:key>', methods=['GET'])
@login_required
def reject_influencer_request(key):
    request = InfluencerRequests.query.get(key)
    request.status = 1
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

# The endpoint for a sponsor to negotiate an influencer request
@app.route('/sponsor/influencer-requests/negotiate/<int:key>', methods=['POST'])
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

# The page for a sponsor to pay an influencer, after an ad request has been completed
@app.route('/sponsor/payment/<int:key>', methods=['GET', 'POST'])
@login_required
def payment(key):
    if request.method == 'GET':
        ad = (
            db.session.query(AdRequests, Influencer, Sponsor)
            .join(Influencer, AdRequests.influencer == Influencer.username)
            .join(Sponsor, AdRequests.sponsor == Sponsor.username)
            .filter(AdRequests.sponsor == current_user.username, AdRequests.status != 4)
            .first()
        )
        return render_template('payment.html', influencer=(ad[1]).name, company=ad[2].company, amount=ad[0].payment, key=key)
    else:
        adrequest = AdRequests.query.get(key)
        adrequest.status = 4
        db.session.commit()
        return redirect(url_for('sponsor_dashboard'))