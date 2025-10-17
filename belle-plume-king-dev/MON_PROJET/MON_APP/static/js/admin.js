(function(){
  // Modal handling
  const modal = document.getElementById('confirm-modal');
  const msgEl = document.getElementById('confirm-message');
  const btnCancel = document.getElementById('confirm-cancel');
  const btnOk = document.getElementById('confirm-ok');
  let activeForm = null;

  // Guard in case script loads before DOM elements
  function initModal(){
    if(!modal || !msgEl || !btnCancel || !btnOk) return false;
    document.querySelectorAll('form.needs-confirm').forEach(f => {
      f.addEventListener('submit', function(e){
        e.preventDefault();
        activeForm = this;
        const message = this.getAttribute('data-message') || 'Confirmer ?';
        msgEl.textContent = message;
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
      });
    });

    btnCancel.addEventListener('click', ()=>{ modal.style.display = 'none'; modal.setAttribute('aria-hidden','true'); activeForm = null; });
    btnOk.addEventListener('click', ()=>{ if(activeForm){ activeForm.submit(); } });
    return true;
  }

  // Toast helper with type support and icons
  function showAdminToast(text, type='', timeout=3500){
    const container = document.getElementById('admin-toast-container');
    if(!container) return;
    const t = document.createElement('div');
    let cls = 'admin-toast';
    if(type) cls += ' admin-toast--' + type;
    t.className = cls;

    // Icon mapping
    let icon = '';
    if(type === 'success') icon = '✓ ';
    else if(type === 'error') icon = '✖ ';
    else if(type === 'warning') icon = '⚠ ';
    else if(type === 'info') icon = 'ℹ ';

    t.textContent = icon + text;
    container.appendChild(t);
    // animate in
    requestAnimationFrame(()=> t.classList.add('show'));
    // remove after timeout
    setTimeout(()=>{ t.classList.remove('show'); setTimeout(()=>t.remove(),300); }, timeout);
  }

  // Show messages passed from server via data attributes and apply type if present
  function showServerMessages(){
    document.querySelectorAll('[data-admin-message]').forEach(el=>{
      const msg = el.getAttribute('data-admin-message');
      const tags = (el.getAttribute('data-admin-message-type') || '').toLowerCase();
      let type = '';
      if(tags.includes('success')) type = 'success';
      else if(tags.includes('error') || tags.includes('danger')) type = 'error';
      else if(tags.includes('warning')) type = 'warning';
      else if(tags.includes('info')) type = 'info';
      showAdminToast(msg, type);
    });
  }

  // Function to handle book edit
  window.editBook = function(bookId) {
    window.location.href = '/admin/books/' + bookId + '/edit/';
  };

  // Initialize when DOM is ready
  if(document.readyState === 'complete' || document.readyState === 'interactive'){
    initModal();
    showServerMessages();
  } else {
    document.addEventListener('DOMContentLoaded', ()=>{
      initModal();
      showServerMessages();
    });
  }

  // Expose utility globally if needed
  window.showAdminToast = showAdminToast;
})();
