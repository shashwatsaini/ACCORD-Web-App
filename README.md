# ACCORD: AI-Powered Influencer Engagement & Sponsorship Coordination Platform

## Description

ACCORD is an AI-powered platform designed to facilitate collaboration between influencers and sponsors for campaign management through ad requests. It features an admin portal providing comprehensive statistics.

## Technologies Used

- **Flask:** Core framework for the web application.
- **Autogen:** Manages the multi-agent system.
- **Flask SQLAlchemy & SQLite:** Database for storing users, campaigns, and requests.
- **Bootstrap & CSS:** For styling the web application.
- **JavaScript:** Frontend validation and dynamic element generation.
- **Flask Login:** Secure user authentication.
- **ChartJS:** Graphs for the admin portal.
- **SwiperJS:** Sliders for campaigns and ad requests.

## Requirements

Install all dependencies through `requirements.txt`. Run the application using `app.py`.

## Features

1. **AI Functionalities:**
   - **Helper Bot:** Fine-tuned Google Gemini model for user assistance.
   - **Profile & Campaign Insights:** Insights for enhanced collaboration.

2. **Core Functionalities:**
   - **Login System:** Unified login for influencers and sponsors with an admin portal.
   - **Admin Portal:** Comprehensive statistics and performance tracking.
   - **Campaign Management:** Create, modify, and delete campaigns.
   - **Ad Request Management:** Send and manage requests between sponsors and influencers.
   - **Search Functionality:** Find influencers and campaigns based on niche.

3. **Additional Features:**
   - Secure login system.
   - Custom styling and aesthetics.
   - Dummy payment portal for ad requests.
   - Data visualization with charts and graphs.
   - Frontend validation.

## Database Schema

### Tables

- **Admin Table**
  - `username`: String, Primary Key
  - `password`: String, Not Null
  - `name`: String

- **Influencer Table**
  - `username`: String, Primary Key
  - `password`: String, Not Null
  - `name`: String
  - `bio`: String
  - `platforms`: String
  - `category`: String
  - `niche`: String
  - `flag`: Integer

- **Sponsor Table**
  - `username`: String, Primary Key
  - `password`: String, Not Null
  - `company`: String
  - `bio`: String
  - `industry`: String
  - `flag`: Integer

- **Campaign Table**
  - `key`: Integer, Primary Key, Auto Increment
  - `sponsor`: String, Foreign Key to Sponsor(username), Not Null
  - `name`: String
  - `description`: String
  - `niche`: String
  - `progress`: Integer
  - `start_date`: Date
  - `end_date`: Date
  - `budget`: Integer
  - `goals`: String
  - `flag`: Integer

- **AdRequests Table**
  - `key`: Integer, Primary Key, Auto Increment
  - `campaign`: Integer, Foreign Key to Campaign(key)
  - `sponsor`: String, Foreign Key to Sponsor(username), Not Null
  - `influencer`: String, Foreign Key to Influencer(username)
  - `description`: String
  - `niche`: String
  - `payment`: Integer
  - `status`: Integer
  - `flag`: Integer

- **SponsorRequests Table**
  - Similar to AdRequests, but stores requests from influencers to sponsors.

- **InfluencerRequests Table**
  - Similar to AdRequests, but stores requests from sponsors to influencers.
   
