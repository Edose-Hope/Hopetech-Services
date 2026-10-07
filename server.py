"""Local runner and private administrator-account setup."""
import argparse
import getpass
from app import app, password_hash, email_field
from database import connect, initialize

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--create-admin', action='store_true')
    parser.add_argument('--init-db', action='store_true')
    args = parser.parse_args()
    # Local runner setup is explicit; the Vercel entrypoint does not run migrations.
    initialize()
    if args.init_db:
        print('Database tables prepared.')
    elif args.create_admin:
        email = email_field({'email': input('Administrator email: ')})
        password = getpass.getpass('Password (12+ characters, at most 72 UTF-8 bytes): ')
        hashed = password_hash(password)
        if password != getpass.getpass('Confirm password: '):
            raise SystemExit('Passwords do not match.')
        with connect() as connection:
            connection.execute('''INSERT INTO admins(email,password) VALUES(?,?)
                ON CONFLICT(email) DO UPDATE SET password=excluded.password''', (email, hashed))
            connection.execute('DELETE FROM sessions WHERE admin_id=(SELECT id FROM admins WHERE email=?)', (email,))
        print('Administrator saved. Existing sessions revoked.')
    else:
        app.run(host=args.host, port=args.port, debug=False)
