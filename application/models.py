from flask_login import UserMixin
from application.database import db

class Admin(db.Model, UserMixin):
    __tablename__ = 'Admin'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False) 
    name = db.Column(db.String)

    def get_id(self):
        return str(self.username)

class Influencer(db.Model, UserMixin):
    __tablename__ = 'Influencer'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    bio = db.Column(db.String)
    platforms = db.Column(db.String)
    category = db.Column(db.String)
    niche = db.Column(db.String)
    flag = db.Column(db.Integer)

    def get_id(self):
        return str(self.username)

class Sponsor(db.Model, UserMixin):
    __tablename__ = 'Sponsor'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)
    company = db.Column(db.String)
    bio = db.Column(db.String)
    industry = db.Column(db.String)
    flag = db.Column(db.Integer)

    def get_id(self):
        return str(self.username)

class AdRequests(db.Model):
    __tablename__ = 'AdRequests'
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign = db.Column(db.Integer, db.ForeignKey('Campaign.key'))
    sponsor = db.Column(db.String, db.ForeignKey('Sponsor.username'), nullable=False)
    influencer = db.Column(db.String, db.ForeignKey('Influencer.username'))
    description = db.Column(db.String)
    niche = db.Column(db.String)
    payment = db.Column(db.Integer)
    status = db.Column(db.Integer)
    flag = db.Column(db.Integer)

    def to_dict(self):
        return {
            'key': str(self.key),
            'sponsor': str(self.sponsor),
            'influencer': str(self.influencer),
            'description': str(self.description),
            'niche': str(self.niche),
            'payment': str(self.payment),
            'status': str(self.status)
        }

class Campaign(db.Model):
    __tablename__ = 'Campaign'
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sponsor = db.Column(db.String, db.ForeignKey('Sponsor.username'), nullable=False)
    name = db.Column(db.String)
    description = db.Column(db.String)
    niche = db.Column(db.String)
    progress = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Integer)
    goals = db.Column(db.String)
    flag = db.Column(db.Integer)

# Requests from influencers to participate in a campaign, before it is converted to an ad request
class InfluencerRequests(db.Model):
    __tablename__ = 'InfluencerRequests'
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer = db.Column(db.String, db.ForeignKey('Influencer.username'), nullable=False)
    sponsor = db.Column(db.String, db.ForeignKey('Sponsor.username'), nullable=False)
    campaign = db.Column(db.Integer, db.ForeignKey('Campaign.key'))
    description = db.Column(db.String)
    niche = db.Column(db.String)
    payment = db.Column(db.Integer)
    status = db.Column(db.Integer)

# Requests from sponsors to influencers to participate in a campaign, before it is converted to an ad request
class SponsorRequests(db.Model):
    __tablename__ = 'SponsorRequests'
    key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer = db.Column(db.String, db.ForeignKey('Influencer.username'), nullable=False)
    sponsor = db.Column(db.String, db.ForeignKey('Sponsor.username'), nullable=False)
    campaign = db.Column(db.Integer, db.ForeignKey('Campaign.key'))
    description = db.Column(db.String)
    niche = db.Column(db.String)
    payment = db.Column(db.Integer)
    status = db.Column(db.Integer)
    