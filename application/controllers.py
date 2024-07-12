from flask import Flask, Blueprint, request
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from datetime import datetime
from application.database import db
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign

@login_manager.user_loader
def load_user(username):
    if Admin.query.get(username):
        return Admin.query.get(username)
    elif Influencer.query.get(username):
        return Influencer.query.get(username)
    elif Sponsor.query.get(username):
        return Sponsor.query.get(username)

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
            print(current_user)
            return redirect(url_for('create_campaign'))
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

@app.route('/sponsor/create-campaign', methods=['GET', 'POST'])
@login_required
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
        return redirect(url_for('sponsor-dashboard.html'))
    