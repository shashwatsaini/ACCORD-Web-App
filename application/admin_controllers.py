from flask import Flask, request
from flask_login import login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from application.database import db
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign, InfluencerRequests, SponsorRequests
from collections import Counter

@login_manager.user_loader
def load_user(username):
    if Admin.query.get(username):
        return Admin.query.get(username)
    elif Influencer.query.get(username):
        return Influencer.query.get(username)
    elif Sponsor.query.get(username):
        return Sponsor.query.get(username)

# The login page for the admin
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
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('adminlogin.html', incorrect=True)

# The dashboard for the admin, displays stats
@app.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'GET':
        unistats = {} # Stats for the universal stats section
        detstats = {} # Stats for the detailed analysis section

        if True:
            # Get universal stats
            unistats['sponsors'] = db.session.query(Sponsor).count()
            unistats['influencers'] = db.session.query(Influencer).count()
            unistats['campaigns'] = db.session.query(Campaign).count()
            unistats['ad_requests'] = db.session.query(AdRequests).count()
            unistats['sponsor_requests'] = db.session.query(SponsorRequests).count()
            unistats['influencer_requests'] = db.session.query(InfluencerRequests).count()
            unistats['budget'] = db.session.query(db.func.sum(Campaign.budget)).scalar()
            unistats['payment'] = db.session.query(db.func.sum(AdRequests.payment)).scalar()

            unistats['top_sponsor'] = db.session.query(Sponsor.company, db.func.count(Campaign.key).label('campaign_count')).join(Campaign, Sponsor.username == Campaign.sponsor).group_by(Sponsor.username).order_by(db.func.count(Campaign.key).desc()).first()
            unistats['top_influencer'] = db.session.query(Influencer.name, db.func.count(AdRequests.key).label('adrequest_count')).join(AdRequests, Influencer.username == AdRequests.influencer).group_by(Influencer.username).order_by(db.func.count(AdRequests.key).desc()).first()
            unistats['top_campaign'] = db.session.query(Campaign.name, Campaign.budget, db.func.count(AdRequests.key).label('adrequest_count')).join(AdRequests, Campaign.key == AdRequests.campaign).group_by(Campaign.key).order_by(db.func.count(AdRequests.key).desc()).first()
        
        if True:
            # Get detailed stats
            # Stats for plotting influencers their niches
            influencers = db.session.query(Influencer).all()
            niches_influencers = [influencer.niche for influencer in influencers]
            niches_influencers = Counter(niches_influencers)
            detstats['niches_influencers'] = (list(niches_influencers.keys()), list(niches_influencers.values()))
            # Stats for plotting campaigns their niches
            campaigns = db.session.query(Campaign).all()
            niches_campaigns = [campaign.niche for campaign in campaigns]
            niches_campaigns = Counter(niches_campaigns)
            detstats['niches_campaigns'] = (list(niches_campaigns.keys()), list(niches_campaigns.values()))
            # Stats for plotting ad requests their niches
            ad_requests = db.session.query(AdRequests).all()
            niches = [ad_request.niche for ad_request in ad_requests]
            niches = Counter(niches)
            detstats['niches'] = (list(niches.keys()), list(niches.values()))
            # Stats for plotting influencers their categories
            categories_influencers = [influencer.category for influencer in influencers]
            categories_influencers = Counter(categories_influencers)
            detstats['categories_influencers'] = (list(categories_influencers.keys()), list(categories_influencers.values()))
            # Stats for plotting cumulative budgets for campaigns
            cumulative_budgets = []
            cumulative_sum = 0
            for campaign in campaigns:
                cumulative_sum += campaign.budget
                cumulative_budgets.append(cumulative_sum)
            detstats['cumulative_budgets'] = cumulative_budgets
            # Stats for plotting cumulative payments for ad requests
            cumulative_payments = []
            cumulative_sum = 0
            for ad_request in ad_requests:
                cumulative_sum += ad_request.payment
                cumulative_payments.append(cumulative_sum)
            detstats['cumulative_payments'] = cumulative_payments

        return render_template('admindashboard.html', unistats=unistats, detstats=detstats)

# The page for sponsors within admin
@app.route('/admin-dashboard/sponsors', methods=['GET', 'POST'])
@login_required
def admin_sponsors():
    if request.method == 'GET':
        campaign_subquery = (
            db.session.query(Campaign.sponsor, db.func.count(Campaign.key).label('campaign_count'))
            .filter(Campaign.progress == 100)
            .group_by(Campaign.sponsor)
            .subquery()
        )
        adrequest_subquery = (
            db.session.query(AdRequests.sponsor, db.func.count(AdRequests.key).label('adrequest_count'))
            .filter(AdRequests.status == 4)
            .group_by(AdRequests.sponsor)
            .subquery()
        )
        sponsors = (
            db.session.query(Sponsor)
            .outerjoin(campaign_subquery, Sponsor.username == campaign_subquery.c.sponsor)
            .outerjoin(adrequest_subquery, Sponsor.username == adrequest_subquery.c.sponsor)
            .add_columns(campaign_subquery.c.campaign_count, adrequest_subquery.c.adrequest_count)
            .all()
        )

        campaigns = (
            db.session.query(Campaign, Sponsor)
            .filter(Campaign.sponsor == Sponsor.username, Campaign.progress != 100)
            .all()
        )
        return render_template('admindashboard-sponsors.html', sponsors=sponsors, campaigns=campaigns)

@app.route('/admin-dashboard/influencers', methods=['GET', 'POST'])
@login_required
def admin_influencers():
    if request.method == 'GET':
        adrequest_subquery = (
            db.session.query(AdRequests.influencer, db.func.count(AdRequests.key).label('adrequest_count'))
            .filter(AdRequests.status == 4)
            .group_by(AdRequests.influencer)
            .subquery()
        )
        influencers = (
            db.session.query(Influencer)
            .outerjoin(adrequest_subquery, Influencer.username == adrequest_subquery.c.influencer)
            .add_columns(adrequest_subquery.c.adrequest_count)
            .all()
        )

        adrequests = db.session.query(AdRequests, Sponsor.company.label('sponsor'), Influencer.name.label('influencer'), Campaign.name.label('campaign')
        ).join(
            Sponsor, AdRequests.sponsor == Sponsor.username
        ).join(
            Influencer, AdRequests.influencer == Influencer.username
        ).join(Campaign, AdRequests.campaign == Campaign.key
        ).filter(AdRequests.status != 4
        ).all()

        return render_template('admindashboard-influencers.html', influencers=influencers, adrequests=adrequests)

# Flagging and unflagging entities
@app.route('/admin-dashboard/flag/<string:type>/<string:key>', methods=['GET'])
@login_required
def admin_flag(type, key):
    # Type can be influencer, sponsor, campaign or an ad request
    # Key is the respective username or key

    if type == 'sponsor':
        sponsor = Sponsor.query.get(key)
        campaigns = Campaign.query.filter(Campaign.sponsor == sponsor.username).all()
        adrequests = AdRequests.query.filter(AdRequests.sponsor == sponsor.username).all()
        if sponsor.flag == 1:
            sponsor.flag = 0
            if campaigns:
                for campaign in campaigns:
                    campaign.flag = 0
            if adrequests:
                for adrequest in adrequests:
                    adrequest.flag = 0
        else:
            sponsor.flag = 1
            for campaign in campaigns:
                campaign.flag = 1
            for adrequest in adrequests:
                adrequest.flag = 1
        db.session.commit()
        return redirect(url_for('admin_sponsors'))
    
    elif type == 'campaign':
        campaign = Campaign.query.get(key)
        adrequests = AdRequests.query.filter(AdRequests.campaign == campaign.key).all()
        if campaign.flag == 1:
            campaign.flag = 0
            if adrequests:
                for adrequest in adrequests:
                    adrequest.flag = 0
        else:
            campaign.flag = 1
            if adrequests:
                for adrequest in adrequests:
                    adrequest.flag = 1
        db.session.commit()
        return redirect(url_for('admin_sponsors'))

    elif type == 'influencer':
        influencer = Influencer.query.get(key)
        adrequests = AdRequests.query.filter(AdRequests.influencer == influencer.username).all()
        if influencer.flag == 1:
            influencer.flag = 0
            if adrequests:
                for adrequest in adrequests:
                    adrequest.flag = 0
        else:
            influencer.flag = 1
            if adrequests:
                for adrequest in adrequests:
                    adrequest.flag = 1
        db.session.commit()
        return redirect(url_for('admin_influencers'))
    
    elif type == 'adrequest':
        adrequest = AdRequests.query.get(key)
        if adrequest.flag == 1:
            adrequest.flag = 0
        else:
            adrequest.flag = 1
        db.session.commit()
        return redirect(url_for('admin_influencers'))

# Deleting entities
@app.route('/admin-dashboard/delete/<string:type>/<string:key>', methods=['GET'])
@login_required
def admin_delete(type, key):
    # Type can be influencer, sponsor, campaign or an ad request
    # Key is the respective username or key

    if type == 'sponsor':
        sponsor = Sponsor.query.get(key)
        campaigns = Campaign.query.filter(Campaign.sponsor == sponsor.username).all()
        ad_requests = AdRequests.query.filter(AdRequests.sponsor == sponsor.username).all()
        if ad_requests:
            for ad_request in ad_requests:
                db.session.delete(ad_request)
        if campaigns:
            for campaign in campaigns:
                db.session.delete(campaign)
        db.session.delete(sponsor)
        db.session.commit()
        return redirect(url_for('admin_sponsors'))
    
    elif type == 'campaign':
        campaign = Campaign.query.get(key)
        ad_requests = AdRequests.query.filter(AdRequests.campaign == campaign.key).all()
        if ad_requests:
            for ad_request in ad_requests:
                db.session.delete(ad_request)
        db.session.delete(campaign)
        db.session.commit()
        return redirect(url_for('admin_sponsors'))
    
    elif type == 'influencer':
        influencer = Influencer.query.get(key)
        ad_requests = AdRequests.query.filter(AdRequests.influencer == influencer.username).all()
        if ad_requests:
            for ad_request in ad_requests:
                db.session.delete(ad_request)
        db.session.delete(influencer)
        db.session.commit()
        return redirect(url_for('admin_influencers'))
    
    elif type == 'adrequest':
        ad_request = AdRequests.query.get(key)
        db.session.delete(ad_request)
        db.session.commit()
        return redirect(url_for('admin_influencers'))
