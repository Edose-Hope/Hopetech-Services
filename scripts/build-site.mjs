import {cpSync,existsSync,mkdirSync,readFileSync,readdirSync,rmSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(import.meta.dirname,'..'),out=resolve(root,'dist');
for(const name of ['corporate/index.html','corporate/corporate.css','corporate/corporate.js','corporate/assets/logo.webp','corporate/assets/favicon.webp','solar/index.html','solar/services-full.html','solar/about.html','solar/script.js']){
 if(!existsSync(resolve(root,name)))throw Error(`Missing website file: ${name}`);
}
rmSync(out,{recursive:true,force:true});mkdirSync(out,{recursive:true});
cpSync(resolve(root,'corporate'),resolve(out,'corporate'),{recursive:true});
cpSync(resolve(root,'corporate/index.html'),resolve(out,'index.html'));
mkdirSync(resolve(out,'solar'),{recursive:true});
for(const name of readdirSync(resolve(root,'solar'))){
 if(/\.(html|css|js|png|jpg|jpeg|webp|mp4|xml|txt)$/i.test(name))cpSync(resolve(root,'solar',name),resolve(out,'solar',name));
}
cpSync(resolve(root,'google2d6faa0d315ebfc4.html'),resolve(out,'google2d6faa0d315ebfc4.html'));
writeFileSync(resolve(out,'robots.txt'),'User-agent: *\nAllow: /\nSitemap: https://hopetechservices.com.ng/sitemap.xml\n');
writeFileSync(resolve(out,'sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://hopetechservices.com.ng/</loc></url></urlset>\n');
const html=readFileSync(resolve(out,'index.html'),'utf8');
if(!html.includes('https://energy.hopetechservices.com.ng/'))throw Error('Corporate website must link to the energy subdomain.');
if(existsSync(resolve(out,'solar/process_form.php')))throw Error('PHP source must not be deployed to static hosting.');
console.log('Built corporate and solar static websites. Training remains on its separate project.');
