// Shared solar interactions; run only when the corresponding page elements exist.
window.topFunction=()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
document.addEventListener('DOMContentLoaded',()=>{
 const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
 const items=document.querySelectorAll('.fade-in-up');
 const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}}),{threshold:.1});
 items.forEach(item=>observer.observe(item));
 const slides=document.querySelectorAll('.slide');let current=0;
 if(slides.length>1&&!reduced&&!new URLSearchParams(location.search).has('energy_preview'))setInterval(()=>{const visible=[...slides].filter(v=>!v.hidden);if(!visible.length)return;slides.forEach(v=>v.classList.remove('active'));current=(current+1)%visible.length;visible[current].classList.add('active');},5000);
 const toggle=document.querySelector('#mobile-menu'),nav=document.querySelector('#nav-menu');
 if(toggle&&nav){
  toggle.setAttribute('role','button');toggle.setAttribute('tabindex','0');toggle.setAttribute('aria-label','Toggle navigation');toggle.setAttribute('aria-controls','nav-menu');toggle.setAttribute('aria-expanded','false');
  const close=()=>{nav.classList.remove('active');toggle.setAttribute('aria-expanded','false');toggle.querySelector('i')?.classList.replace('fa-times','fa-bars');};
  toggle.addEventListener('click',()=>{const open=!nav.classList.contains('active');nav.classList.toggle('active',open);toggle.setAttribute('aria-expanded',String(open));const icon=toggle.querySelector('i');if(icon){icon.classList.toggle('fa-bars',!open);icon.classList.toggle('fa-times',open);}});
  toggle.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();toggle.click();}});
  nav.addEventListener('click',event=>{if(event.target.closest('a'))close();});
  document.addEventListener('keydown',event=>{if(event.key==='Escape')close();});
 }
 const top=document.querySelector('#backToTopBtn');if(top){top.addEventListener('click',window.topFunction);const scroll=()=>{top.style.display=scrollY>300?'block':'none';};addEventListener('scroll',scroll,{passive:true});scroll();}
 const form=document.querySelector('#pro-contact-form');
 if(form){
  const button=form.querySelector('[type=submit]'),status=document.querySelector('#form-status');
  form.addEventListener('submit',async event=>{
   event.preventDefault();if(button.disabled)return;const original=button.textContent;button.disabled=true;button.textContent='Sending…';status.textContent='';
   try{
    const response=await fetch(form.action,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});
    if(!response.ok)throw Error('Unable to send your enquiry. Please try again or call our team.');
    status.textContent='Thank you. Your enquiry has been sent to our team.';form.reset();
   }catch(error){status.textContent=error.message||'Unable to connect. Please try again or call our team.';}
   finally{button.disabled=false;button.textContent=original;}
  });
 }
});
