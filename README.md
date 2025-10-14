# Coderr

Coderr is a Django-based platform designed to offer and manage various services. It provides user authentication, service listings, order handling, reviews, and profile management within a modular architecture.

## Features

- User authentication and registration
- Service offering and management
- Order creation and tracking
- Review system for services and providers
- Profile management for users and service providers

## Requirements

- Python 3.10 or higher
- Django 4.x
- pip (Python package manager)
- Virtual environment (recommended)

## Setup Guide

### Clone the repository

git clone https://github.com/Hellsticks96/coderr.git
cd coderr

### Create and activate a virtual environment

python -m venv venv
source venv/bin/activate # on macOS/Linux
venv\Scripts\activate # on Windows

### Install dependencies

pip install -r requirements.txt

### Apply migrations

python manage.py migrate

### Run the development server

python manage.py runserver

### Access the application

Open your browser and go to:

http://127.0.0.1:8000/

### Project Structure

coderr/
│
├── core/ # Core project settings and URLs
├── offers/ # Handles service offerings
├── orders/ # Manages service orders
├── profiles/ # User and provider profiles
├── reviews/ # Service review system
├── user_auth_app/ # Authentication and user management
├── requirements.txt # Project dependencies
└── manage.py # Django management script

### Development

To run tests or make changes:

python manage.py test

# Create a superuser for admin access

python manage.py createsuperuser

### License

This project is open source and available under the MIT License
.
