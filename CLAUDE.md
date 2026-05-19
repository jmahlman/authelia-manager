# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Authelia-Manager is a Flask web UI for managing Authelia configuration. It provides a browser-based interface to configure Authelia's user database, access control rules, networks, and SMTP/notification settings without manually editing YAML files.

The project is in active early development.

## Development Commands

### Run locally

```bash
./run.sh
```

This creates a `.venv`, installs dependencies, and starts uWSGI on port 5000.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uwsgi --http 0.0.0.0:5000 --wsgi-file authelia-manager.py --callable app --workers 4 --uid 1000 --gid 1000
```

### Docker

```bash
docker compose up
```

Exposes port 9999 mapped to internal port 5000.

### Initialize the database

Hit `/api/initdb` in the browser after starting the app. This creates the SQLite database at `instance/authelia-manager.sqlite`.

## Architecture

### Entry point

`authelia-manager.py` imports the Flask `app` from `app/__init__.py`, which configures Flask, SQLAlchemy, and Flask-Login, then registers two blueprints.

### Blueprints

- **`app/blueprints/api.py`** — REST API and authentication endpoints (`/api/*`). Handles login/logout, CRUD for users/networks/rules/groups/totp, password generation, and serving current Authelia YAML/JSON config.
- **`app/blueprints/ui.py`** — UI routes (`/`, `/ui`, `/edit/<data>`, `/config`, `/users`, `/networks`, `/rules`). Each renders a Jinja2 template.

### Models (`app/models/`)

SQLAlchemy models backed by SQLite:
- `config` — full Authelia configuration (hostname, JWT, sessions, SMTP, access control defaults)
- `users` — application users (login credentials, groups)
- `group`, `networks`, `rules`, `totp`, `host`, `file_auth`

Schema details are documented in `app/models/MODELS.md`.

### Helpers (`app/helpers/`)

- `argon2hash.py` — Argon2 password hashing and verification
- `rndpwd.py` — random password generation
- `apidocs.py` — renders API documentation from markdown
- `iterateQuery.py` — converts SQLAlchemy query results to dicts

### Frontend

- Templates: `app/templates/` (Jinja2 HTML)
- Static JS: `app/static/js/` — handles UI interactions (accordions, API communication, dynamic form add/remove)
- Authelia config data files: `app/data/` (YAML files read by the config viewer endpoints)

### Authentication

Flask-Login with Argon2id password hashing. Sessions expire after 30 minutes of inactivity.
