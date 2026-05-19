# Connecting Authelia-Manager to Authelia

This guide covers how to deploy authelia-manager alongside your Authelia instance so you can manage its configuration through the web UI.

## Overview

Authelia-manager needs access to two things from your Authelia deployment:

1. **`configuration.yml`** — Authelia's main config (access control rules, session settings, SMTP, etc.)
2. **`users_database.yml`** — The file-based user database

These are mounted into the authelia-manager container as volumes.

## Docker Compose Setup

Below is a compose file that runs authelia-manager alongside Authelia. Adjust paths to match your setup.

```yaml
services:
  authelia-manager:
    image: ghcr.io/jmahlman/authelia-manager:latest
    container_name: authelia-manager
    ports:
      - 9999:5000
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./authelia/configuration.yml:/app/app/data/configuration.yml
      - ./authelia/users_database.yml:/app/app/data/users_database.yml
    restart: unless-stopped

  authelia:
    image: authelia/authelia:latest
    container_name: authelia
    volumes:
      - ./authelia:/config
    ports:
      - 9091:9091
    environment:
      - TZ=America/New_York
    restart: unless-stopped
```

### Key points

- Both containers share the same Authelia config files via volume mounts.
- Authelia reads from `/config/`, authelia-manager reads from `/app/app/data/`.
- Changes made in authelia-manager are written to the shared volume, so Authelia picks them up on restart.

## Standalone Setup (Manager Only)

If Authelia is running on a different host, copy its config files to a local directory and mount them:

```yaml
services:
  authelia-manager:
    image: ghcr.io/jmahlman/authelia-manager:latest
    container_name: authelia-manager
    ports:
      - 9999:5000
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - /path/to/your/authelia/configuration.yml:/app/app/data/configuration.yml
      - /path/to/your/authelia/users_database.yml:/app/app/data/users_database.yml
    restart: unless-stopped
```

## First-Time Setup

### 1. Add the `authelia-manager` group to your Authelia users

In your Authelia `users_database.yml`, add the `authelia-manager` group to any user that should have access to the management UI:

```yaml
users:
    myuser:
        password: $argon2id$v=19$m=4096,t=3,p=1$...
        displayname: My User
        email: myuser@example.com
        groups:
            - admins
            - authelia-manager
        disabled: false
```

### 2. Start the container

```bash
docker compose up -d
```

On startup, authelia-manager automatically reads the mounted `users_database.yml` and imports any users in the `authelia-manager` group into its internal database. Their Authelia password hash is reused, so they log in with the same credentials.

### 3. Log in

Go to `http://localhost:9999/ui/login` and log in with your Authelia credentials.

Users are re-synced on every container restart. If you add or remove users from the `authelia-manager` group, or change passwords in Authelia, restart the container to pick up the changes.

### Alternative: Manual user creation

If you prefer not to use the auto-seed (or need a standalone admin user not in Authelia), you can create one manually:

```bash
docker exec -it authelia-manager python3 -c "
from app import app, db
from app.helpers.argon2hash import argon2hash

with app.app_context():
    db.create_all()
    from app.models.users import users
    pw = argon2hash('your-password-here').generate()
    admin = users(
        user='admin',
        display='Administrator',
        email='admin@example.com',
        groups='admins',
        hash=pw['hash']
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully')
"
```

Replace `your-password-here` with your desired password.

## Protecting Authelia-Manager with Authelia

To put authelia-manager behind Authelia itself (so you get 2FA on the management UI), add an access control rule to your Authelia `configuration.yml`:

```yaml
access_control:
  rules:
    - domain: "authelia-manager.example.com"
      policy: two_factor
      subject:
        - "group:admins"
```

Then configure your reverse proxy (Traefik, nginx, Caddy) to route `authelia-manager.example.com` to the authelia-manager container on port 5000, with Authelia as the authentication middleware.

### Traefik example (docker labels)

```yaml
services:
  authelia-manager:
    image: ghcr.io/jmahlman/authelia-manager:latest
    container_name: authelia-manager
    environment:
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./authelia/configuration.yml:/app/app/data/configuration.yml
      - ./authelia/users_database.yml:/app/app/data/users_database.yml
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.authelia-manager.rule=Host(`authelia-manager.example.com`)"
      - "traefik.http.routers.authelia-manager.entrypoints=websecure"
      - "traefik.http.routers.authelia-manager.tls.certresolver=letsencrypt"
      - "traefik.http.routers.authelia-manager.middlewares=authelia@docker"
      - "traefik.http.services.authelia-manager.loadbalancer.server.port=5000"
    restart: unless-stopped
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session signing key. Set to a random string for persistent sessions across restarts. | Random on each start |
| `DATABASE_URI` | SQLAlchemy database URI | `sqlite:///authelia-manager.sqlite` |

## File Paths Inside the Container

| Path | Purpose |
|------|---------|
| `/app/app/data/configuration.yml` | Authelia main config (mount your real one here) |
| `/app/app/data/users_database.yml` | Authelia user database (mount your real one here) |
| `/app/instance/authelia-manager.sqlite` | Internal SQLite DB (manager users/sessions) |

## Troubleshooting

**"Database is missing" error on login**
Run the init script from the First-Time Setup section above.

**Changes not reflected in Authelia**
Authelia doesn't hot-reload config. Restart the Authelia container after making changes: `docker restart authelia`

**Permission denied on mounted files**
The container runs as uid 1000. Ensure your mounted config files are readable/writable by uid 1000:
```bash
chown 1000:1000 ./authelia/configuration.yml ./authelia/users_database.yml
```
