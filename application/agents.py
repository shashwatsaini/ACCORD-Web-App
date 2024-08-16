import autogen
import os
from application.config import APIKeys
from flask import current_app as app

llm_config = APIKeys.llm_config

chat_assistant = autogen.ConversableAgent(
    'chat-assistant',
    system_message='OBJECTIVE: You are the ACCORD Helper Bot for ACCORD, a Sponsor & Influencer Collaboration Platform.\\nn'
                   'INPUT: You will receive the user message and the documentation of the platform, which you must read and understand to help the user.\n\n'
                   'METHODS: \n'
                        '1. You will understand the user query.\n'
                        '2. You will then peruse the documentation to find a solution. Core functionalities and features can be found easily.\n'
                            'The documentation also contains information on methods, for influencers & sponsors, refer to their endpoint and overview as well.\n'
                   'OUTPUT: Your output must be in plaintext, do not output markup, HTML, or links. Keep conversation to a minimum.\n\n',
                   #'IMPORTANT: Do not respond to messages that are not explained in the documentation or those that seem irrelevant to the platform.\n'
                   #'In such cases, you must respond with "I am sorry, I cannot help." Do not refer to the documentation',
    llm_config=llm_config,
    human_input_mode='NEVER',
    code_execution_config=False
)

user_proxy = autogen.UserProxyAgent(
    'user-proxy',
    human_input_mode='NEVER',
    code_execution_config=False
)
