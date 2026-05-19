# 2026/05/19
Modernization update for Python 3.13+ compatibility (forward-compatible with 3.14)

## CI/CD
- Added GitHub Actions workflow to build and push container to ghcr.io on push
- Image published to `ghcr.io/jmahlman/authelia-manager` (replaces `beardedtek/authelia-manager:demo`)
- Tags: branch name, semver on tags (v*), git SHA, and `latest` on main
- Updated `docker-compose.yml` to use new ghcr.io image
- Upgraded compose file from version 3 syntax to modern format

## Dependencies
- Pinned all dependencies to minimum modern versions
- Removed `passlib` (unused, argon2-cffi handles all hashing)
- Added `flask-wtf` for CSRF protection
- Added `markupsafe` as explicit dependency
- Updated minimum versions: Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6.3, PyYAML 6.0.2, uwsgi 2.0.28

## Security Fixes
- Replaced hardcoded SECRET_KEY with environment variable (`SECRET_KEY` env var with random fallback)
- Added CSRF protection via Flask-WTF across all POST routes
- Added `SESSION_COOKIE_HTTPONLY` and `SESSION_COOKIE_SAMESITE` settings
- Made `DATABASE_URI` configurable via environment variable
- Replaced insecure `random` module with `secrets` module in password generation (rndpwd.py)
- Replaced `random.randint` with `secrets.randbelow` in API responses
- Added `@login_required` to `/api/initdb` and `/api/<data>` POST endpoints

## Code Fixes
- Removed deprecated `flask.escape` import (removed in Flask 2.4+)
- Removed duplicate `request` import in api.py
- Fixed bare `except:` clause to use `except Exception:` and `except ImportError:`
- Removed all debug `print()` statements from production code
- Removed redundant `SQLALCHEMY_TRACK_MODIFICATIONS` assignment
- Deleted obsolete `app/helpers/argon2.py.old`

## Dockerfile
- Updated base image from `python:3.11` to `python:3.13-slim`
- Added non-root user (appuser, uid 1000)
- Added build dependencies for uwsgi compilation
- Improved layer caching (COPY requirements.txt before app code)
- Enabled uWSGI master process and threads

## Entrypoint
- Rewrote `entrypoint.sh` (was broken, contained only `apt-update`)
- Now properly launches uwsgi with master mode and threading

## Security Scan Results
- Ran `bandit` scan: 0 high/medium issues, 1 low (test-only hardcoded password in argon2hash.py __main__ block)
- Ran `pip-audit`: 0 known vulnerabilities in updated dependencies

# 2023/04/20
Much progress has been made
- Restructured database
  - host
  - users
  - groups
  - networks
  - rules
  - totp
  - file_auth
  - config
- JavaScript
  - async code to display and send form data to API
- API
  - Starting to write database queries for updating entries
    - only for users so far
- UI
  - MAJOR UI overhauls.  Using tailwind and flowbite for css and form controls
  - Notifications
- More
  - Lots more than I can remember at this point.  I should have written this as I go...


# 2022/12/18
Initial code dump to database
- Database Models created
    - acc_networks - holds network definitions
    - acc_rules - holds rules definitions
    - config - holds main configuration.yml contents (other than networks and rules)
- API Blueprint created
    - Routes:
        - /api - Lists api endpoints
        - /api/initdb - Initializes Database
        - api/config `GET` - lists current config
            - For now in JSON format, will make it look pretty once the core code is done
        - api/config `POST` - NOT YET CREATED - This will be the endpoint that updates the database with a POST message.
- helpers
    - argon2 - generates an argon2 password given input.  See app/helpers/argon2.py for more info
    - rndpwd - generates a random passphrase or seed. See app/helpers/rndpwd.py for more info
        - taken and slightly modified from beardedtek-com/fevr (another one of my projects)
