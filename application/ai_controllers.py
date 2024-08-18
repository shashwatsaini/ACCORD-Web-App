import os
from flask import Flask, request, jsonify
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from application.database import db
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign, InfluencerRequests, SponsorRequests

import autogen
from application.agents import chat_assistant, profile_insights_assistant, campaign_insights_assistant, user_proxy
from application.config import APIKeys, AgentGuide
llm_config = APIKeys.llm_config
agent_guide = AgentGuide.agent_guide

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')

    chat_outline = {
        'sender': user_proxy,
        'recipient': chat_assistant,
        'message': f'This is the user message: {user_message}. This is the documentation: {agent_guide}',
        'summary_method': 'last_msg',
        'max_turns': 1,
        'clear_history': True
    }

    chat = autogen.initiate_chats([chat_outline])
    reply = chat[-1].summary

    return jsonify({"response": reply})

@app.route('/profile_insights', methods=['GET'])
def profile_insights():
    username = request.args.get('username')

    chat_outline = {
        'sender': user_proxy,
        'recipient': profile_insights_assistant,
        'summary_method': 'last_msg',
        'max_turns': 1,
        'clear_history': True
    }

    if Sponsor.query.get(username):
        user = Sponsor.query.get(username)
        campaigns = db.session.query(Campaign.description).filter_by(sponsor=user.username).all()
        ad_requests = db.session.query(AdRequests.description).filter_by(sponsor=user.username).all()

        chat_outline['message'] = f'Sponsor User: {user.company}, User Profile: {user.bio}, Campaigns: {campaigns}, Ad Requests: {ad_requests}'
        chat = autogen.initiate_chats([chat_outline])
        reply = chat[-1].summary

        return jsonify({"response": reply})

    elif Influencer.query.get(username):
        user = Influencer.query.get(username)
        ad_requests = db.session.query(AdRequests.description).filter_by(influencer=user.username).all()

        chat_outline['message'] = f'Influencer User: {user.name}, User Profile: {user.bio}, Ad Requests: {ad_requests}'
        chat = autogen.initiate_chats([chat_outline])
        reply = chat[-1].summary

        return jsonify({"response": reply})
    
    else:
        return jsonify({"response": "There is an error with AI Insights, please try later."})
    
@app.route('/campaign_insights', methods=['GET'])
def campaign_insights():
    key = request.args.get('key')
    campaign = Campaign.query.get(key)
    ad_requests = db.session.query(AdRequests.description).filter_by(campaign=key).all()

    chat_outline = {
        'sender': user_proxy,
        'recipient': campaign_insights_assistant,
        'message': f'Campaign: {campaign.name}, Campaign Description: {campaign.description}, Ad Requests: {ad_requests}',
        'summary_method': 'last_msg',
        'max_turns': 1,
        'clear_history': True
    }

    chat = autogen.initiate_chats([chat_outline])
    reply = chat[-1].summary
    return jsonify({"response": reply})
