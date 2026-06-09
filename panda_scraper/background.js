chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

chrome.tabs.onActivated.addListener(({ tabId }) => {
  chrome.tabs.get(tabId, (tab) => {
    if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) return;
    chrome.sidePanel.setOptions({ tabId, path: 'panel.html', enabled: true });
  });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status !== 'complete') return;
  if (!tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://')) return;
  chrome.sidePanel.setOptions({ tabId, path: 'panel.html', enabled: true });

  // Notify panel that the page has navigated
  chrome.runtime.sendMessage({ type: 'PAGE_NAVIGATED', tabId, url: tab.url }).catch(() => {});
});

// Relay messages between content script and panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CONTENT_TO_PANEL') {
    chrome.runtime.sendMessage({ ...message.payload, _from: 'content', tabId: sender.tab?.id })
      .catch(() => {});
  }
  if (message.type === 'PANEL_TO_CONTENT') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs[0]) {
        chrome.tabs.sendMessage(tabs[0].id, message.payload, (res) => {
          sendResponse(res);
        });
      }
    });
    return true;
  }
});
