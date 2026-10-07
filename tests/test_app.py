import http.cookiejar, json, os, secrets, sys, tempfile, threading, unittest
from urllib.parse import urlsplit
from unittest.mock import patch
import psycopg
from pathlib import Path
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app as application
import database
from werkzeug.serving import make_server

class ApplicationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory()
  test_url=os.environ.get('HOPETECH_TEST_POSTGRES_URL')
  cls.environment=patch.dict(os.environ,{},clear=False);cls.environment.start()
  for key in ('POSTGRES_URL','POSTGRES_URL_NON_POOLING','VERCEL','VERCEL_ENV'):os.environ.pop(key,None)
  if test_url:
   parsed=urlsplit(test_url)
   if parsed.hostname not in ('127.0.0.1','localhost') or parsed.path!='/hopetech_test':raise RuntimeError('Tests require the dedicated loopback hopetech_test database.')
   os.environ['POSTGRES_URL']=test_url;os.environ['HOPETECH_LOCAL_POSTGRES']='1'
   with psycopg.connect(test_url) as c:c.execute('DROP SCHEMA IF EXISTS hopetech CASCADE')
  else:
   database.SQLITE_PATH=Path(cls.temp.name)/'test.sqlite3'
  database.initialize()
  cls.password=secrets.token_urlsafe(20)
  with database.connect() as c:c.execute('INSERT INTO admins(email,password) VALUES(?,?)',('admin@example.com',application.password_hash(cls.password)))
  cls.http=make_server('127.0.0.1',0,application.app,threaded=True);cls.base=f'http://127.0.0.1:{cls.http.server_port}'
  threading.Thread(target=cls.http.serve_forever,daemon=True).start()
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.temp.cleanup();cls.environment.stop()
 def setUp(self):self.client=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def request(self,path,method='GET',data=None,csrf=None):
  headers={'Content-Type':'application/json'}
  if csrf:headers['X-CSRF-Token']=csrf
  req=Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
  try:r=self.client.open(req)
  except HTTPError as e:r=e
  with r:return r.status,json.loads(r.read())
 def login(self):
  status,data=self.request('/api/login','POST',{'email':'admin@example.com','password':self.password});self.assertEqual(status,200);return data['csrf']
 def payload(self,email):return {'name':'Test Learner','email':email,'phone':'+2349050000000','course':'web-design-php','schedule':'weekend','consent':True}
 def test_database_health_and_schema_repeatability(self):
  self.assertEqual(self.request('/api/health'),(200,{'database':'ready'}))
  database.initialize()
  self.assertEqual(self.request('/api/health')[0],200)
 def test_production_refuses_sqlite_fallback(self):
  with patch.dict(os.environ,{'VERCEL':'1','POSTGRES_URL':'','POSTGRES_URL_NON_POOLING':''}):
   self.assertEqual(self.request('/api/health')[0],503)
   self.assertEqual(self.request('/api/catalog')[0],200)
 def test_cross_origin_and_expired_sessions(self):
  token=self.login()
  req=Request(self.base+'/api/students',data=json.dumps(self.payload('cross-origin@example.com')).encode(),headers={'Content-Type':'application/json','Origin':'https://evil.example','X-CSRF-Token':token},method='POST')
  with self.assertRaises(HTTPError) as result:self.client.open(req)
  self.assertEqual(result.exception.code,403)
  with database.connect() as c:c.execute('UPDATE sessions SET expires=0')
  self.assertEqual(self.request('/api/students')[0],401)
 def test_expired_rate_limit_resets_and_blocks_at_limit(self):
  from app import rate_limit
  with application.app.test_request_context('/api/contact',environ_base={'REMOTE_ADDR':'192.0.2.12'}):
   rate_limit('isolated-test',2,60);rate_limit('isolated-test',2,60)
   from werkzeug.exceptions import TooManyRequests
   with self.assertRaises(TooManyRequests):rate_limit('isolated-test',2,60)
   with database.connect() as c:c.execute("UPDATE limits SET expires=0 WHERE key LIKE 'isolated-test:%'")
   rate_limit('isolated-test',2,60)
 def test_secure_hosted_cookie(self):
  with patch.dict(os.environ,{'HOPETECH_SECURE_COOKIE':'1'}):
   with application.app.test_client() as client:
    response=client.post('/api/login',json={'email':'admin@example.com','password':self.password})
    self.assertEqual(response.status_code,200)
    cookie=response.headers['Set-Cookie']
    self.assertIn('Secure;',cookie);self.assertIn('HttpOnly;',cookie);self.assertIn('SameSite=Strict',cookie)
 def test_public_pages_and_private_paths(self):
  for p in ('/','/about','/courses','/schedule','/contact','/register','/admin'):
   with self.client.open(self.base+p) as r:self.assertEqual(r.status,200);self.assertIn(b'Hopetech',r.read())
  for path in ('/server.py','/data/hopetech.sqlite3','/.git/config'):
   with self.assertRaises(HTTPError):self.client.open(self.base+path)
 def test_registration_persists_and_duplicate_rejected(self):
  p=self.payload('persistent@example.com');self.assertEqual(self.request('/api/register','POST',p)[0],201)
  self.assertEqual(self.request('/api/register','POST',p)[0],409)
  with database.connect() as c:self.assertEqual(c.execute('SELECT name FROM students WHERE email=?',(p['email'],)).fetchone()['name'],p['name'])
 def test_validation_and_consent(self):
  p=self.payload('invalid@example.com');p['consent']=False;self.assertEqual(self.request('/api/register','POST',p)[0],400)
  p['consent']=True;p['course']='fake';self.assertEqual(self.request('/api/register','POST',p)[0],400)
  p['course']='web-design-php';p['email']='bad';self.assertEqual(self.request('/api/register','POST',p)[0],400)
 def test_admin_authentication_and_csrf(self):
  self.assertEqual(self.request('/api/students')[0],401)
  self.assertEqual(self.request('/api/login','POST',{'email':'admin@example.com','password':'wrong'})[0],401)
  token=self.login();self.assertEqual(self.request('/api/students')[0],200)
  self.assertEqual(self.request('/api/students','POST',self.payload('blocked@example.com'))[0],403)
  self.assertEqual(self.request('/api/logout','POST',{},token)[0],200)
  self.assertEqual(self.request('/api/students')[0],401)
 def test_student_management(self):
  token=self.login();status,data=self.request('/api/students','POST',self.payload('managed@example.com'),token);self.assertEqual(status,201)
  path='/api/students/'+str(data['id']);self.assertEqual(self.request(path,'PATCH',{'status':'Confirmed'},token)[0],200)
  rows=self.request('/api/students')[1]['students'];self.assertEqual(next(s for s in rows if s['id']==data['id'])['status'],'Confirmed')
  self.assertEqual(self.request(path,'DELETE',{},token)[0],200);self.assertEqual(self.request(path,'DELETE',{},token)[0],404)
 def test_enquiries_are_private(self):
  self.assertEqual(self.request('/api/contact','POST',{'name':'Enquiry','email':'hello@example.com','message':'Course question'})[0],201)
  self.assertEqual(self.request('/api/messages')[0],401);self.login();self.assertTrue(any(m['message']=='Course question' for m in self.request('/api/messages')[1]['messages']))
 def test_browser_registration_and_dashboard(self):
  from playwright.sync_api import sync_playwright
  with sync_playwright() as p:
   b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   for path,heading in [('/','Small steps. Big possibilities.'),('/about','Technology is for everyone.'),('/courses','Find your next skill.'),('/schedule','Make room for your future.'),('/contact','Let’s talk about your next step.')]:
    page.goto(self.base+path);page.get_by_role('heading',name=heading).wait_for();self.assertEqual(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),True)
   page.goto(self.base+'/courses');page.get_by_role('button',name='Programming',exact=True).click();self.assertEqual(page.locator('.course-card').count(),13)
   for path in ('/','/about','/courses','/schedule','/contact','/register','/admin'):
    page.set_viewport_size({'width':390,'height':844});page.goto(self.base+path);page.locator('header').wait_for();self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),path)
   page.goto(self.base+'/');page.get_by_role('button',name='Open navigation').click();page.get_by_role('navigation').get_by_role('link',name='Courses',exact=True).click();page.get_by_role('heading',name='Find your next skill.').wait_for()
   page.goto(self.base+'/register?course=web-design-php&schedule=weekend');page.get_by_label('Full name').fill('Browser Learner');page.get_by_label('Email address',exact=True).fill('browser@example.com');page.get_by_label('Phone number').fill('+2349050000000');page.locator('[name=consent]').check();page.get_by_role('button',name='Submit registration').click();page.get_by_text('Registration received.',exact=False).wait_for()
   page.goto(self.base+'/admin');page.get_by_label('Email address',exact=True).fill('admin@example.com');page.get_by_label('Password',exact=True).fill(self.password);page.get_by_role('button',name='Sign in',exact=False).click();page.get_by_role('heading',name='Student directory').wait_for();page.get_by_role('searchbox').fill('Browser Learner');self.assertEqual(page.locator('#student-rows tr').count(),1)
   page.get_by_label('Status for Browser Learner').select_option('Confirmed');page.get_by_role('heading',name='Student directory').wait_for();page.get_by_role('button',name='Add student',exact=False).click();dialog=page.get_by_role('dialog');dialog.get_by_label('Full name').fill('Added by Admin');dialog.get_by_label('Email address',exact=True).fill('added@example.com');dialog.get_by_label('Phone number').fill('+2349050000001');dialog.get_by_label('Preferred course').select_option('data-analysis-excel');dialog.get_by_label('Learning schedule').select_option('weekday');dialog.get_by_role('button',name='Save student').click();page.get_by_text('Added by Admin',exact=True).wait_for();page.get_by_role('button',name='Sign out').click();page.get_by_role('heading',name='Administrator login').wait_for();self.assertEqual(errors,[]);b.close()
if __name__=='__main__':unittest.main(verbosity=2)
