# Coderr API

A REST API for a freelance services marketplace. Business users create tiered service offers, customers place orders, and both sides can manage profiles and reviews.

Built with Django REST Framework and deployed on Railway with separate staging and production environments.

**Live API:** _link coming soon_  
**API Docs (Swagger UI):** _link coming soon_

---

## Tech Stack

- **Django 5** / **Django REST Framework**
- **PostgreSQL** (production) / SQLite (local)
- **Token authentication**
- **Railway** (hosting + CI/CD)
- **GitHub Actions** (automated testing on every PR)
- **drf-spectacular** (OpenAPI schema + Swagger UI)
- **WhiteNoise** (static file serving)
- **Ruff** (linting + formatting)

---

## Features

- User registration and token-based authentication
- Business users can create service packages with basic, standard, and premium tiers
- Customers can browse offers and place orders
- Order lifecycle management (in progress → completed / cancelled)
- Review system with duplicate prevention
- Profile management for both user types
- Platform-wide stats endpoint (review count, average rating, offer count)

---

## Local Development

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
git clone https://github.com/Hellsticks96/coderr.git
cd coderr

python -m venv env

# Mac/Linux
source env/bin/activate

# Windows
env\Scripts\activate

pip install -r requirements.txt
```

### Git hooks

```bash
# Mac/Linux
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

# Windows
git config core.hooksPath .githooks
git update-index --chmod=+x .githooks/pre-commit
```

The pre-commit hook runs linting and formatting checks before every commit.

### Environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

`SECRET_KEY` is required. `DEBUG` and `ALLOWED_HOSTS` fall back to safe defaults if omitted. `DATABASE_URL` is optional locally — omitting it uses SQLite.

### Run

```bash
python manage.py migrate
python manage.py runserver
```

Swagger UI: http://127.0.0.1:8000/api/schema/swagger-ui/

---

## Testing

```bash
python manage.py test --verbosity=2
```

Tests run automatically via GitHub Actions on every push and pull request to `main`. Dependabot keeps dependencies up to date with weekly scans.

---

## Project Structure

```
coderr/
├── coderr/          # Project config (settings, URLs, WSGI)
├── core/            # Platform stats endpoint
├── offers/          # Service packages and offer details
├── orders/          # Order creation and management
├── profiles/        # User and business profiles
├── reviews/         # Review system
├── user_auth_app/   # Custom user model and authentication
└── tests/           # Shared test utilities
```

---

## Deployment

Deployed on [Railway](https://railway.app) via `railway.toml`. Two environments are configured — staging and production — each with its own Railway service and PostgreSQL instance.

Railway runs `collectstatic` and `migrate` automatically on each deploy.

### Environment variables (Railway dashboard)

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Your Railway domain |
| `DATABASE_URL` | Set automatically when a Postgres service is attached |

### CI/CD

GitHub Actions secret required:  
**Settings → Secrets and variables → Actions → New repository secret**  
Name: `SECRET_KEY`, value: any secure random string

---

## License

MIT
