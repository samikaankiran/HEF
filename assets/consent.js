(function(){var K='hef-consent',v=null,bar=document.getElementById('consent');try{v=localStorage.getItem(K)}catch(e){}
function load(){document.querySelectorAll('[data-map-src]').forEach(function(w){if(w.dataset.loaded)return;w.dataset.loaded='1';var f=document.createElement('iframe');f.className='map';f.title=w.dataset.mapTitle;f.src=w.dataset.mapSrc;f.setAttribute('loading','lazy');f.setAttribute('referrerpolicy','no-referrer-when-downgrade');f.setAttribute('allowfullscreen','');w.replaceChildren(f)})}
function show(){if(!bar)return;bar.hidden=false;requestAnimationFrame(function(){requestAnimationFrame(function(){bar.classList.add('in')})})}
function hide(){if(!bar)return;bar.classList.remove('in');setTimeout(function(){bar.hidden=true},500)}
document.addEventListener('click',function(e){var t=e.target.closest('[data-consent]');if(!t)return;var a=t.getAttribute('data-consent');if(a==='open'){try{localStorage.removeItem(K)}catch(x){}show();return}try{localStorage.setItem(K,a)}catch(x){}hide();if(a==='accepted')load()});
if(v==='accepted')load();else if(!v)show()})();
