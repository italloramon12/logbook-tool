// background.js - ActivityTracker Browser Extension
const API_URL = "http://localhost:5001/api/log_event";
let currentTab = null;
let tabStartTime = {};
let tabInfo = {};
let typingBuffer = {};
let searchQueries = [];

// Envia evento para a API
async function logEvent(type, title, detail, duration = 0) {
  try {
    const data = {
      ts: Math.floor(Date.now() / 1000),
      type: type,
      title: title,
      detail: detail,
      duration: duration
    };
    
    await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    
    console.log("Event logged:", data);
  } catch (error) {
    console.error("Failed to log event:", error);
  }
}

// Detecta tipo de site
function categorizeUrl(url) {
  const urlLower = url.toLowerCase();
  
  if (urlLower.includes('web.whatsapp.com')) return 'whatsapp';
  if (urlLower.includes('web.telegram.org') || urlLower.includes('telegram.org')) return 'telegram';
  if (urlLower.includes('facebook.com') || urlLower.includes('fb.com')) return 'facebook';
  if (urlLower.includes('instagram.com')) return 'instagram';
  if (urlLower.includes('twitter.com') || urlLower.includes('x.com')) return 'twitter';
  if (urlLower.includes('linkedin.com')) return 'linkedin';
  if (urlLower.includes('youtube.com')) return 'youtube';
  if (urlLower.includes('netflix.com')) return 'netflix';
  if (urlLower.includes('github.com')) return 'github';
  if (urlLower.includes('stackoverflow.com')) return 'stackoverflow';
  if (urlLower.includes('google.com/search')) return 'google_search';
  
  return 'website';
}

// Extrai query de busca da URL
function extractSearchQuery(url) {
  try {
    const urlObj = new URL(url);
    
    // Google
    if (urlObj.hostname.includes('google.com')) {
      return urlObj.searchParams.get('q');
    }
    
    // Bing
    if (urlObj.hostname.includes('bing.com')) {
      return urlObj.searchParams.get('q');
    }
    
    // DuckDuckGo
    if (urlObj.hostname.includes('duckduckgo.com')) {
      return urlObj.searchParams.get('q');
    }
    
    // YouTube
    if (urlObj.hostname.includes('youtube.com') && urlObj.pathname.includes('/results')) {
      return urlObj.searchParams.get('search_query');
    }
    
    return null;
  } catch (e) {
    return null;
  }
}

// Registra tempo gasto em uma aba
function recordTabTime(tabId) {
  if (tabStartTime[tabId] && tabInfo[tabId]) {
    const duration = Math.floor((Date.now() - tabStartTime[tabId]) / 1000);
    if (duration > 2) { // só registra se passou mais de 2 segundos
      const siteType = categorizeUrl(tabInfo[tabId].url || '');
      
      // Log com categoria específica
      logEvent(
        siteType,
        tabInfo[tabId].title || "Sem título",
        tabInfo[tabId].url || "unknown",
        duration
      );
      
      // Se tem query de busca, registra separadamente
      const searchQuery = extractSearchQuery(tabInfo[tabId].url);
      if (searchQuery && !searchQueries.includes(searchQuery)) {
        searchQueries.push(searchQuery);
        logEvent(
          "search",
          "Busca: " + searchQuery,
          tabInfo[tabId].url,
          0
        );
      }
    }
  }
}

// Monitora mudanças de aba ativa
browser.tabs.onActivated.addListener(async (activeInfo) => {
  // Registra tempo da aba anterior
  if (currentTab !== null && currentTab !== activeInfo.tabId) {
    recordTabTime(currentTab);
  }
  
  // Nova aba ativa
  currentTab = activeInfo.tabId;
  tabStartTime[currentTab] = Date.now();
  
  // Obtém informações da aba
  try {
    const tab = await browser.tabs.get(currentTab);
    tabInfo[currentTab] = {
      url: tab.url,
      title: tab.title
    };
    
    // Log de início com categoria
    const siteType = categorizeUrl(tab.url);
    logEvent(siteType, tab.title || "Sem título", `started:${tab.url}`, 0);
    
    // Se for busca, registra query
    const searchQuery = extractSearchQuery(tab.url);
    if (searchQuery) {
      logEvent("search", "Busca: " + searchQuery, tab.url, 0);
    }
  } catch (error) {
    console.error("Error getting tab info:", error);
  }
});

// Monitora atualizações de aba (mudança de URL ou título)
browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.title) {
    // Se for a aba ativa, registra tempo da URL anterior
    if (tabId === currentTab && changeInfo.url) {
      recordTabTime(tabId);
      tabStartTime[tabId] = Date.now();
    }
    
    // Atualiza informações
    tabInfo[tabId] = {
      url: tab.url,
      title: tab.title
    };
    
    // Log de mudança
    if (tabId === currentTab) {
      const siteType = categorizeUrl(tab.url);
      logEvent(siteType, tab.title || "Sem título", `navigated:${tab.url}`, 0);
      
      // Registra busca se houver
      const searchQuery = extractSearchQuery(tab.url);
      if (searchQuery && !searchQueries.includes(searchQuery)) {
        searchQueries.push(searchQuery);
        logEvent("search", "Busca: " + searchQuery, tab.url, 0);
      }
    }
  }
});

// Monitora fechamento de abas
browser.tabs.onRemoved.addListener((tabId) => {
  recordTabTime(tabId);
  delete tabStartTime[tabId];
  delete tabInfo[tabId];
  
  if (currentTab === tabId) {
    currentTab = null;
  }
});

// Monitora mudanças de janela
browser.windows.onFocusChanged.addListener((windowId) => {
  if (windowId === browser.windows.WINDOW_ID_NONE) {
    // Navegador perdeu foco, registra tempo
    if (currentTab !== null) {
      recordTabTime(currentTab);
      currentTab = null;
    }
  } else {
    // Navegador ganhou foco, pega aba ativa
    browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
      if (tabs.length > 0) {
        currentTab = tabs[0].id;
        tabStartTime[currentTab] = Date.now();
        tabInfo[currentTab] = {
          url: tabs[0].url,
          title: tabs[0].title
        };
      }
    });
  }
});

// Registra tempo ao fechar o navegador
browser.runtime.onSuspend.addListener(() => {
  if (currentTab !== null) {
    recordTabTime(currentTab);
  }
});

// Recebe mensagens do content script
browser.runtime.onMessage.addListener((message, sender) => {
  if (message.action === 'logInput') {
    const data = message.data;
    
    if (message.type === 'text_input') {
      // Registra texto digitado
      logEvent(
        data.site,
        `Input em ${data.site}`,
        `text_length:${data.length}`,
        0
      );
    } else if (message.type === 'form_submit') {
      // Registra formulário enviado
      logEvent(
        'form_submit',
        'Formulário enviado',
        `${data.fields} campos em ${data.url}`,
        0
      );
    }
  }
});

// Inicialização
browser.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
  if (tabs.length > 0) {
    currentTab = tabs[0].id;
    tabStartTime[currentTab] = Date.now();
    tabInfo[currentTab] = {
      url: tabs[0].url,
      title: tabs[0].title
    };
    console.log("ActivityTracker extension initialized");
  }
});
