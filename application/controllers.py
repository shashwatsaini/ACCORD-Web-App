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
            return redirect(url_for('influencer-dashboard.html'))
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

@app.route('/sponsor/dashboard', methods=['GET', 'POST'])
#@login_required
def sponsor_dashboard():
    if request.method == 'GET':
        campaigns = Campaign.query.filter_by(sponsor='sponsor').all()
        influencer_requests = db.session.query(InfluencerRequests, Campaign.name).join(Campaign).filter(InfluencerRequests.sponsor == 'sponsor', InfluencerRequests.status == 0).all()[::-1]
        past_influencer_requests = db.session.query(InfluencerRequests, Campaign.name).join(Campaign).filter(InfluencerRequests.sponsor == 'sponsor', InfluencerRequests.status != 0).all()[::-1]
        return render_template('sponsordashboard.html', campaigns=campaigns, influencer_requests=influencer_requests, past_influencer_requests=past_influencer_requests)

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
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/influencer-requests/reject/<int:key>', methods=['GET'])
#@login_required
def reject_influencer_request(key):
    request = InfluencerRequests.query.get(key)
    request.status = 1
    db.session.commit()
    return redirect(url_for('sponsor_dashboard'))

@app.route('/sponsor/payment', methods=['GET', 'POST'])
#@login_required
def payment(adrequests_key=0):
    if request.method == 'GET':
        return render_template('payment.html', influencer='Dummy', company='Dummy', amount=100)
    else:
        adrequest = AdRequests.query.get(adrequests_key)
        adrequest.status = 3
        db.session.commit()
        return redirect(url_for('sponsor-dashboard.html'))

@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    