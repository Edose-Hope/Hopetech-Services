import {cpSync, existsSync, mkdirSync} from 'node:fs';
import {resolve} from 'node:path';
const root=resolve(import.meta.dirname,'..');
const source=resolve(root,'public');
for(const name of ['index.html','about.html','courses.html','schedule.html','contact.html','register.html','admin.html','app.js','style.css','assets/logo.png','assets/courses-and-prices.pdf']){
 if(!existsSync(resolve(source,name)))throw new Error(`Missing public asset: ${name}`);
}
const output=resolve(root,'dist');
mkdirSync(output,{recursive:true});
cpSync(source,output,{recursive:true});
console.log('Public website built in dist/. Private server files and databases are not copied.');
