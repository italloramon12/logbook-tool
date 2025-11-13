// background.js - ActivityTracker Browser Extension (Manifest V3)
const API_URL = "http://localhost:5001/api/log_event";
let currentTab = null;
let tabStartTime = {};
let tabInfo = {};

// Compatibilidade Chrome/Firefox
const browserAPI = typeof chrome !== 'undefined' ? chrome : browser;

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
    // Não falha silenciosamente - API pode estar offline
  }
}

// Registra tempo gasto em uma aba
function recordTabTime(tabId) {
  if (tabStartTime[tabId] && tabInfo[tabId]) {
    const duration = Math.floor((Date.now() - tabStartTime[tabId]) / 1000);
    if (duration > 2) { // só registra se passou mais de 2 segundos
      logEvent(
        "website",
        tabInfo[tabId].title || "Sem título",
        tabInfo[tabId].url || "unknown",
        duration
      );
    }
  }
}

// Monitora mudanças de aba ativa
browserAPI.tabs.onActivated.addListener(async (activeInfo) => {
  // Registra tempo da aba anterior
  if (currentTab !== null && currentTab !== activeInfo.tabId) {
    recordTabTime(currentTab);
  }
  
  // Nova aba ativa
  currentTab = activeInfo.tabId;
  tabStartTime[currentTab] = Date.now();
  
  // Obtém informações da aba
  try {
    const tab = await browserAPI.tabs.get(currentTab);
    tabInfo[currentTab] = {
      url: tab.url,
      title: tab.title
    };
    
    // Log de início
    logEvent("website", tab.title || "Sem título", `started:${tab.url}`, 0);
  } catch (error) {
    console.error("Error getting tab info:", error);
  }
});

// Monitora atualizações de aba (mudança de URL ou título)
browserAPI.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
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
      logEvent("website", tab.title || "Sem título", `navigated:${tab.url}`, 0);
    }
  }
});

// Monitora fechamento de abas
browserAPI.tabs.onRemoved.addListener((tabId) => {
  recordTabTime(tabId);
  delete tabStartTime[tabId];
  delete tabInfo[tabId];
  
  if (currentTab === tabId) {
    currentTab = null;
  }
});

// Monitora mudanças de janela
browserAPI.windows.onFocusChanged.addListener((windowId) => {
  if (windowId === browserAPI.windows.WINDOW_ID_NONE) {
    // Navegador perdeu foco, registra tempo
    if (currentTab !== null) {
      recordTabTime(currentTab);
      currentTab = null;
    }
  } else {
    // Navegador ganhou foco, pega aba ativa
    browserAPI.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
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

// Registra tempo ao fechar o navegador (Manifest V3)
if (browserAPI.runtime.onSuspend) {
  browserAPI.runtime.onSuspend.addListener(() => {
    if (currentTab !== null) {
      recordTabTime(currentTab);
    }
  });
}

// Recebe mensagens do content script
browserAPI.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'logInput') {
    const tab = sender.tab;
    logEvent(
      "text_input",
      `${message.type} - ${tab.title}`,
      `${message.data.site}: ${message.data.length} chars`,
      0
    );
  }
});

// Inicialização
browserAPI.tabs.query({ active: true, currentWindow: true }).then((tabs) => {
  if (tabs.length > 0) {
    currentTab = tabs[0].id;
    tabStartTime[currentTab] = Date.now();
    tabInfo[currentTab] = {
      url: tabs[0].url,
      title: tabs[0].title
    };
  }
});
