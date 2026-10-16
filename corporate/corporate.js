(() => {
 const toggle=document.querySelector('.menu-toggle');const nav=document.querySelector('#main-nav');
 function close(){toggle.setAttribute('aria-expanded','false');nav.classList.remove('open');}
 toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
 nav.addEventListener('click',event=>{if(event.target.closest('a'))close();});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'){close();toggle.focus();}});
 document.querySelector('#year').textContent=new Date().getFullYear();
 // The solar and corporate domains share a deployment, with separate page routing.
 const solarBase=document.documentElement.dataset.solarUrl||'https://energy.hopetechservices.com.ng/';
 document.querySelectorAll('[data-solar-link]').forEach(a=>{const hash=new URL(a.href).hash;a.href=solarBase+hash;});
})();
