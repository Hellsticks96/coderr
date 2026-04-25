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
- Django 5.x
- pip (Python package manager)
- Virtual environment (recommended)

## Setup Guide

### Clone the repository

```bash
git clone https://github.com/Hellsticks96/coderr.git
cd coderr
```

### Development Setup

After cloning the repo, run the following commands to enable the Git hooks:

**Mac/Linux:**

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

**Windows:**

```bash
git config core.hooksPath .githooks
git update-index --chmod=+x .githooks/pre-commit
```

This sets up a pre-commit hook that checks linting and formatting before every commit.

### Create and activate a virtual environment

**Mac/Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**

```cmd
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

`SECRET_KEY` is required. `DEBUG` and `ALLOWED_HOSTS` fall back to safe defaults if omitted.

### Apply migrations

```bash
python manage.py migrate
```

### Run the development server

```bash
python manage.py runserver
```

### Access the application

Open your browser and go to:

http://127.0.0.1:8000/

### Running tests

```bash
python manage.py test --verbosity=2
```

Tests also run automatically via GitHub Actions on every push and pull request to `main`.

### Linting and formatting

```bash
ruff check .        # check for lint errors
ruff format .       # auto-format code
```

The pre-commit hook runs both checks automatically before every commit.

### GitHub Actions setup

The CI workflow requires a `SECRET_KEY` secret to be set in your repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `SECRET_KEY`, value: any secure random string

## Project Structure

```
coderr/
│
├── coderr/          # Django project config (settings, URLs, WSGI)
├── core/            # Platform stats API
├── offers/          # Service offerings and details
├── orders/          # Order creation and management
├── profiles/        # User and business profiles
├── reviews/         # Review system
├── user_auth_app/   # Authentication and user model
├── tests/           # Shared test utilities
├── requirements.txt # Project dependencies
└── manage.py        # Django management script
```

## License

This project is open source and available under the MIT License.
