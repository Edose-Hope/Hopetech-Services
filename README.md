# Hopetech Services ICT website

Responsive Home, About Us, Courses, Training Schedule, Contact, Registration, and Administrator pages. Student registrations and contact enquiries persist in a database. Administrators can add/search students, update enrolment status, delete records after confirmation, and export CSV.

The application is prepared for **Vercel Python Functions + Supabase PostgreSQL**, with SQLite retained for local development. Deployment steps for the owner are in [DEPLOYMENT.md](DEPLOYMENT.md). The code and tables are prepared locally; they have not been pushed to GitHub, applied to the user's Supabase project, or deployed to Vercel by Codex.

## Local development

Python 3.12 is pinned. Create a virtual environment and install the pinned packages:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py --port 8080
```

The local runner creates missing SQLite tables in `data/hopetech.sqlite3`. Create or reset a private local administrator account with:

```sh
.venv/bin/python server.py --create-admin
```

The password is entered with a hidden prompt, has at least 12 characters, and is never echoed. No default administrator exists. Existing local scrypt accounts remain supported; new accounts use bcrypt.

## Application structure

- `app.py`: Flask routes, validation, login, CSRF protection, database-backed rate limits, and student/enquiry APIs.
- `database.py`: PostgreSQL/SQLite connection handling; Vercel refuses SQLite fallback.
- `catalog.py`: 32 confirmed courses, NGN fees, student prices, durations, and learning-schedule preferences.
- `public/`: responsive pages, local logo, scripts, styles, and the supplied PDF price list.
- `api/index.py`, `vercel.json`: Vercel function entrypoint and routing/build configuration.
- `package.json`, `package-lock.json`, `scripts/build.mjs`: dependency-free Node 24 static build to `dist/`.
- `database/schema.sql`, `database/create-admin.sql`: Supabase setup and protected first-admin creation.

The previous solar HTML/PHP files at the repository root are retained. They are not the new application; do not use the former PHP server to run it.

## Business information

The 32 courses, standard fees, student prices, and durations match the supplied PDF. Web Design with Python & Django deliberately retains ₦200,000 for both prices as supplied, pending the owner's clarification. Student-rate eligibility remains subject to confirmation. Opening hours are Monday–Friday 8am–5pm, Saturday 9am–4pm (WAT); individual class dates/times and online availability remain unconfirmed.

Address: Magnus Alozie Close, No 1 Wodi New Layout, Road, off Inter-Lock, Rumuwaji, Elelenwo.
Contact: info.hopetechservices@gmail.com, +234 702 602 4460.
Domain: https://hopetechservices.com.ng/.
The local logo is cropped from the existing repository logo and can be replaced at `public/assets/logo.png`.

## Configuration and protection of records

In Vercel, the existing Supabase integration supplies `POSTGRES_URL` in Production. No extra secret is required by the code. `POSTGRES_URL_NON_POOLING` is a server-side fallback; pooled connections are preferred. `SUPABASE_URL`, JWT secrets, and public browser keys are not needed by this backend. Configure database URL values privately in the hosting environment; never commit `.env` files or share URLs/passwords in chat.

For local development, no database URL means SQLite. For Vercel, a missing URL returns service-unavailable errors instead of saving records to temporary files. PostgreSQL connections require verified TLS using system CA roots, disable prepared statements for transaction-pooler compatibility, and close promptly. The private `hopetech` schema denies browser-role access and has row-level security enabled. Only the server's database-owner connection accesses it.

Registration requires consent and rejects duplicate email/course entries. Statuses are Pending, Confirmed, Completed, and Cancelled. Sessions expire after eight hours; tokens are hashed in the database. Mutations require CSRF checks; cross-origin browser submissions are rejected. Parameterized SQL, escaped UI values, bounded requests, and server-side validation protect inputs. API responses are never cached. Passwords and personal data are not included in application error logs.

Contact messages are stored privately for the team to review and respond to; automated email delivery and payments are not implemented. Protect database backups and define your organisation's record-retention policy before collecting real student data. Use Supabase's appropriate backup/restore options for the cloud database. For local SQLite, use its backup API rather than copying a file during active writes. Local data and backups are ignored by Git and Vercel upload rules.

## Tests

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check public/app.js
```

The default run uses temporary SQLite and random test-only credentials: 12 workflow/security tests run; 2 PostgreSQL-only setup tests are skipped. Browser tests need Playwright for Python and Chromium at `/usr/bin/chromium` (available in the current cloud machine).

To exercise the same workflows plus the actual setup scripts using an isolated local PostgreSQL, set `HOPETECH_TEST_POSTGRES_URL` to the dedicated `hopetech_test` database on loopback. These tests refuse remote/production URLs and clear only the private test schema. For example, with a local test server already running:

```sh
HOPETECH_TEST_POSTGRES_URL=postgresql://agent@127.0.0.1:55432/hopetech_test .venv/bin/python -m unittest discover -s tests -v
```

Never use a live Supabase project as a test target. `HOPETECH_LOCAL_POSTGRES=1` disables TLS only for loopback local PostgreSQL, and is refused for remote hosts or on Vercel. It is set by the tests, not needed for deployment. Hosted connectivity, real administrator setup, and live registration still require validation after owner setup and deployment.
