"""Checks the actual Supabase setup scripts against an isolated local PostgreSQL."""
import os, secrets, unittest
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import patch
import psycopg
import app as application
import database

@unittest.skipUnless(os.environ.get('HOPETECH_TEST_POSTGRES_URL'), 'Requires the dedicated local PostgreSQL test database')
class PostgreSQLSetupTests(unittest.TestCase):
 def setUp(self):
  url=os.environ['HOPETECH_TEST_POSTGRES_URL'];parsed=urlsplit(url)
  if parsed.hostname not in ('127.0.0.1','localhost') or parsed.path!='/hopetech_test':raise RuntimeError('Only the dedicated loopback test database is allowed.')
  self.environment=patch.dict(os.environ,{'POSTGRES_URL':url,'HOPETECH_LOCAL_POSTGRES':'1','POSTGRES_URL_NON_POOLING':''});self.environment.start();self.addCleanup(self.environment.stop)
  database.initialize()
 def test_browser_roles_cannot_access_private_tables(self):
  with database.connect() as c:
   for role in ('anon','authenticated'):
    self.assertFalse(c.execute('SELECT has_schema_privilege(?, ?, ?) AS allowed',(role,'hopetech','USAGE')).fetchone()['allowed'])
    for table in ('admins','students','sessions','messages','limits'):
     self.assertFalse(c.execute('SELECT has_table_privilege(?, ?, ?) AS allowed',(role,'hopetech.'+table,'SELECT')).fetchone()['allowed'])
   count=c.execute("SELECT count(*) AS total FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='hopetech' AND c.relrowsecurity").fetchone()['total']
   self.assertEqual(count,5)
 def test_sql_admin_setup_guards_placeholders_and_login_works(self):
  script=(Path(__file__).resolve().parents[1]/'database/create-admin.sql').read_text()
  with self.assertRaises(psycopg.errors.RaiseException):
   with database.connect() as c:c.connection.execute(script,prepare=False)
  password=secrets.token_urlsafe(20)
  seed=script.replace('REPLACE_WITH_YOUR_EMAIL','sql-admin@example.invalid').replace('REPLACE_WITH_A_PRIVATE_PASSWORD',password)
  with database.connect() as c:c.connection.execute(seed,prepare=False)
  with application.app.test_client() as client:
   result=client.post('/api/login',json={'email':'sql-admin@example.invalid','password':password})
   self.assertEqual(result.status_code,200)
   self.assertEqual(client.get('/api/students').status_code,200)
  with database.connect() as c:
   self.assertNotEqual(c.execute('SELECT password FROM admins WHERE email=?',('sql-admin@example.invalid',)).fetchone()['password'],password)
