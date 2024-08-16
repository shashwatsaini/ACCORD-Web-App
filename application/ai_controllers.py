import os
from flask import Flask, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import login_manager
from flask import render_template, request, redirect, url_for
from flask import current_app as app
from application.models import Admin, Influencer, Sponsor, AdRequests, Campaign, InfluencerRequests, SponsorRequests

import autogen
from application.agents import chat_assistant, user_proxy
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
