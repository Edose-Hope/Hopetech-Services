# Put the Hopetech ICT website on Vercel

The Supabase integration is connected to `hopetech-services`. Your screenshot shows `POSTGRES_URL` and the other Supabase variables in Vercel's **Production** environment. Codex cannot read these remote values from the screenshot. Keep them private; do not paste them into chat or GitHub.

## 1. Create the database tables

1. Open Supabase and choose **Hopetech Project**.
2. Open **SQL Editor** → **New query**.
3. Open `database/schema.sql` from the prepared code and copy the entire file.
4. Paste it into the SQL Editor and click **Run**.
5. A successful result may say **Success. No rows returned**. This is expected.

The script creates the `hopetech` schema and the five tables. It does not delete existing records. Re-running the same script is safe. Keep the `hopetech` schema out of the Supabase **exposed schemas** list; the web app accesses it only through its server-side PostgreSQL connection. Browser `anon` and `authenticated` roles are denied access, and row-level security is enabled on every table.

## 2. Create your private administrator login

1. Open another new Supabase SQL query.
2. Copy the complete `database/create-admin.sql` file into it.
3. Replace `REPLACE_WITH_YOUR_EMAIL` with the email you want to use to log in.
4. Replace `REPLACE_WITH_A_PRIVATE_PASSWORD` with a unique password of at least 12 characters (no more than 72 UTF-8 bytes). Keep the surrounding single quotes. If your password contains a single quote, enter it as two single quotes inside the SQL string.
5. Click **Run**. The script refuses to run with the placeholders unchanged.
6. Remove the private password from the SQL Editor afterwards. Do not save/share the edited query, show it in screenshots, or put it into GitHub.

This creates the account with a bcrypt hash. Re-running it with the same email resets that account's password and revokes its login sessions. It does not reset other accounts. There is no public administrator sign-up or shared default password.

## 3. Publish the prepared code

The prepared application files must be committed and pushed to the connected **Edose-Hope/Hopetech-Services** GitHub repository. They are currently in the Codex workspace; installing integrations does not upload code. Updating Vercel's Production branch can immediately replace the live website, so review the prepared changes before publishing.

The new root `vercel.json` explicitly builds `api/index.py` as a Python Function and builds `public/` into static pages using `scripts/build.mjs` and Node 24. Vercel installs pinned Python dependencies from `requirements.txt`; the static build has no npm dependencies. Python 3.12 is specified in `.python-version`. The old solar-site files at the root are preserved but no longer used by these routes. Keep Vercel's project Root Directory at the repository root.

The server uses `POSTGRES_URL` (falling back to `POSTGRES_URL_NON_POOLING`) from your existing integration. Use the Supabase-provided pooled URL for serverless requests. TLS certificate verification stays enabled. Database connections are closed after each transaction, and prepared statements are disabled for compatibility with transaction pooling. Vercel automatically uses Secure, HttpOnly, SameSite session cookies. No Supabase service-role key or JWT secret is sent to the browser.

Your screenshot only establishes **Production** variables. Preview deployments need their own configured database before forms/login can work. Prefer a separate test database for previews. Do not put your production password or database URL into chat to enable this.

## 4. Check the deployed website

After Vercel reports a successful deployment:

- Check the five public pages, logo, contact details, all 32 course prices, and the price-list download.
- Open `/api/health`: `{"database":"ready"}` indicates the function can read the required tables. A 503 means the database URL, TLS connection, permissions, or schema still needs investigation; it does not prove registration works.
- Log in at `/admin` using your own account and verify that student records/enquiries are visible only when signed in.
- Submit one clearly labelled test registration, then confirm it appears in the dashboard. Remove the test record afterwards. This stores data only; it does not send email or take payment.
- Sign out and verify `/api/students` returns 401.

Do not share student records or passwords in diagnostic screenshots. Database-backed Vercel behavior has not been validated against your live Supabase project yet. Local tests use an isolated PostgreSQL database, not your production data.
