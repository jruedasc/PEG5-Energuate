document.addEventListener('DOMContentLoaded', function(){
  const btn = document.getElementById('btn-change-pwd');
  const campos = document.getElementById('pwd-fields');
  if (btn){
    btn.addEventListener('click', () => {
      const visible = campos.style.display !== 'none';
      campos.style.display = visible ? 'none' : 'flex';
      campos.querySelectorAll('input').forEach(i => {
        if (visible) {
          i.removeAttribute('required');
          i.value = '';
        } else {
          i.setAttribute('required','');
        }
      });
    });
  }
});
