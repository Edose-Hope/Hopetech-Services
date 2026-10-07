-- Run schema.sql first. Use the Supabase SQL Editor, never chat or GitHub, for passwords.
-- Replace BOTH placeholder strings below before running this file.
-- Choose a unique password of 12+ characters and no more than 72 UTF-8 bytes.
-- This creates or resets ONLY the specified administrator and revokes their sessions.
CREATE SCHEMA IF NOT EXISTS extensions;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA extensions;
SET search_path TO hopetech, extensions, public;
DO $create_admin$
DECLARE
    admin_email text := 'REPLACE_WITH_YOUR_EMAIL';
    admin_password text := 'REPLACE_WITH_A_PRIVATE_PASSWORD';
    saved_admin_id bigint;
BEGIN
    IF admin_email LIKE 'REPLACE_%' OR admin_password LIKE 'REPLACE_%' THEN
        RAISE EXCEPTION 'Replace both placeholders with your own email and private password first.';
    END IF;
    admin_email := lower(btrim(admin_email));
    IF admin_email !~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$' OR length(admin_email) > 254 THEN
        RAISE EXCEPTION 'Enter a valid email address.';
    END IF;
    IF length(admin_password) < 12 OR octet_length(admin_password) > 72 THEN
        RAISE EXCEPTION 'Use a password of at least 12 characters and at most 72 UTF-8 bytes.';
    END IF;
    INSERT INTO hopetech.admins(email, password)
    VALUES (admin_email, crypt(admin_password, gen_salt('bf', 12)))
    ON CONFLICT(email) DO UPDATE SET password = excluded.password
    RETURNING id INTO saved_admin_id;
    DELETE FROM hopetech.sessions WHERE admin_id = saved_admin_id;
END
$create_admin$;
RESET search_path;
-- Passwords are stored as hashes, not as plaintext. Clear the private password
-- from the SQL Editor afterwards; do not save/share the edited query.
