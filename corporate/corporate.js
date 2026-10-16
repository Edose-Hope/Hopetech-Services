(() => {
 const toggle=document.querySelector('.menu-toggle');const nav=document.querySelector('#main-nav');
 function close(){toggle.setAttribute('aria-expanded','false');nav.classList.remove('open');}
 toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});
 nav.addEventListener('click',event=>{if(event.target.closest('a'))close();});
 document.addEventListener('keydown',event=>{if(event.key==='Escape'){close();toggle.focus();}});
 document.querySelector('#year').textContent=new Date().getFullYear();
 // Until the solar subdomain has DNS and HTTPS, the preserved site remains available on this host.
 const solarBase=document.documentElement.dataset.solarUrl||'/solar/';
 document.querySelectorAll('[data-solar-link]').forEach(a=>{const hash=new URL(a.href).hash;a.href=solarBase+hash;});
})();
