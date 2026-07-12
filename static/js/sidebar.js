const sidebar=document.querySelector('#sidebar');
const overlay=document.querySelector('#sidebarOverlay');
const toggleButton=document.querySelector('#menuToggle');
function setSidebar(open){sidebar?.classList.toggle('open',open);overlay?.classList.toggle('open',open);document.body.classList.toggle('nav-open',open);toggleButton?.setAttribute('aria-expanded',String(open));}
toggleButton?.setAttribute('aria-expanded','false');
toggleButton?.addEventListener('click',()=>setSidebar(!sidebar?.classList.contains('open')));
overlay?.addEventListener('click',()=>setSidebar(false));
sidebar?.querySelectorAll('nav a').forEach(link=>link.addEventListener('click',()=>setSidebar(false)));
document.addEventListener('keydown',event=>{if(event.key==='Escape')setSidebar(false)});
