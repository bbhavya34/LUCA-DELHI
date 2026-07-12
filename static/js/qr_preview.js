document.querySelector('input[type=file]')?.addEventListener('change',e=>{const p=document.querySelector('[data-preview]');if(p&&e.target.files[0])p.src=URL.createObjectURL(e.target.files[0])});
