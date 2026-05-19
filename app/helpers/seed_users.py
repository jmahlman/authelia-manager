import yaml
from os import path, getcwd


def seed_users_from_authelia(app, db):
    users_file = path.join(getcwd(), 'app', 'data', 'users_database.yml')
    if not path.isfile(users_file):
        return

    with open(users_file) as f:
        data = yaml.safe_load(f)

    if not data or 'users' not in data:
        return

    from app.models.users import users

    with app.app_context():
        db.create_all()
        for username, info in data['users'].items():
            if info.get('disabled', False):
                continue
            groups = info.get('groups', [])
            if 'authelia-manager' not in groups:
                continue

            existing = users.query.filter_by(user=username).first()
            groups_str = ','.join(groups)
            if existing:
                existing.display = info.get('displayname', username)
                existing.email = info.get('email', '')
                existing.groups = groups_str
                existing.hash = info.get('password', '')
            else:
                new_user = users(
                    user=username,
                    display=info.get('displayname', username),
                    email=info.get('email', ''),
                    groups=groups_str,
                    hash=info.get('password', '')
                )
                db.session.add(new_user)

        db.session.commit()
