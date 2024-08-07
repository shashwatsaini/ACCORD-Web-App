from flask import Flask, request
from flask_login import login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign, InfluencerRequests, SponsorRequests

# Needed for flask-login, loads in users from the database
@login_manager.user_loader
def load_user(username):
    if Admin.query.get(username):
        return Admin.query.get(username)
    elif Influencer.query.get(username):
        return Influencer.query.get(username)
    elif Sponsor.query.get(username):
        return Sponsor.query.get(username)

# Status codes for the ad requests
status = {0: 'Pending', 1:'Rejected', 2:'Accepted', 3:'Completed, Pending Payment', 4:'Completed'}
# Status codes for the influencer and sponsor requests
request_state = {0: 'Pending', 1: 'Rejected', 2: 'Accepted'}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('userlogin.html', incorrect=0, flag=0)
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        # The login system checks if the user is an admin, influencer, or sponsor
        # All users have a unique username, despite being stored in different tables, this check is implemented on registration

        if Influencer.query.filter_by(username=username, password=password).first():
            user = Influencer.query.filter_by(username=username).first()
            if user.flag == 0:
                login_user(load_user(username))
                return redirect(url_for('influencer_dashboard'))
            else:
                return render_template('userlogin.html', incorrect=0, flag=1)
        elif Sponsor.query.filter_by(username=username, password=password).first():
            user = Sponsor.query.filter_by(username=username).first()
            if user.flag == 0:
                login_user(load_user(username))
                return redirect(url_for('sponsor_dashboard'))   
            else:
                return render_template('userlogin.html', incorrect=0, flag=1)
        else:
            return render_template('userlogin.html', incorrect=1, flag=0)     

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
    