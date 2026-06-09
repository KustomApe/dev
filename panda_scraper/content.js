(() => {
  if (window.__pandaScraperLoaded) return;
  window.__pandaScraperLoaded = true;

  // ─── State ────────────────────────────────────────────────────────────────
  let inspectMode = false;
  let hoveredEl = null;
  let selectedElements = [];
  let overlay = null;

  // ─── Overlay tooltip ─────────────────────────────────────────────────────
  function createOverlay() {
    const el = document.createElement('div');
    el.id = '__panda_overlay__';
    el.style.cssText = `
      position:fixed;bottom:16px;left:50%;transform:translateX(-50%);
      background:#1a1a2e;color:#e0e0e0;padding:6px 14px;border-radius:20px;
      font:13px/1.5 monospace;z-index:2147483647;pointer-events:none;
      box-shadow:0 4px 20px rgba(0,0,0,.5);opacity:0;transition:opacity .15s;
      max-width:80vw;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    `;
    document.body.appendChild(el);
    return el;
  }

  function showOverlay(text) {
    if (!overlay) overlay = createOverlay();
    overlay.textContent = text;
    overlay.style.opacity = '1';
  }

  function hideOverlay() {
    if (overlay) overlay.style.opacity = '0';
  }

  // ─── Highlight styles ─────────────────────────────────────────────────────
  const HOVER_STYLE = '2px solid #7c3aed';
  const SELECT_STYLE = '2px solid #10b981';
  const HOVER_BG = 'rgba(124,58,237,.08)';
  const SELECT_BG = 'rgba(16,185,129,.08)';

  function applyHover(el) {
    if (!el || el === document.body) return;
    el.__pandaOrigOutline = el.style.outline;
    el.__pandaOrigBg = el.style.backgroundColor;
    el.style.outline = HOVER_STYLE;
    el.style.backgroundColor = HOVER_BG;
  }

  function removeHover(el) {
    if (!el) return;
    el.style.outline = el.__pandaOrigOutline ?? '';
    el.style.backgroundColor = el.__pandaOrigBg ?? '';
  }

  function applySelect(el) {
    el.__pandaOrigOutline = el.style.outline;
    el.__pandaOrigBg = el.style.backgroundColor;
    el.style.outline = SELECT_STYLE;
    el.style.backgroundColor = SELECT_BG;
  }

  function removeSelect(el) {
    el.style.outline = el.__pandaOrigOutline ?? '';
    el.style.backgroundColor = el.__pandaOrigBg ?? '';
  }

  // ─── CSS Selector generation ──────────────────────────────────────────────
  function getUniqueCssSelector(el) {
    if (el.id) return `#${CSS.escape(el.id)}`;

    const path = [];
    let current = el;

    while (current && current.nodeType === Node.ELEMENT_NODE && current !== document.body) {
      let selector = current.tagName.toLowerCase();

      // Try unique class combo
      if (current.classList.length > 0) {
        const classSelector = selector + '.' + [...current.classList]
          .filter(c => !c.startsWith('__panda'))
          .map(c => CSS.escape(c))
          .join('.');
        const matches = document.querySelectorAll(classSelector);
        if (matches.length === 1) {
          path.unshift(classSelector);
          break;
        }
      }

      // nth-child fallback
      const parent = current.parentElement;
      if (parent) {
        const siblings = [...parent.children].filter(c => c.tagName === current.tagName);
        if (siblings.length > 1) {
          const idx = siblings.indexOf(current) + 1;
          selector += `:nth-of-type(${idx})`;
        }
      }

      path.unshift(selector);
      current = current.parentElement;
    }

    if (!path.length) return el.tagName.toLowerCase();
    return path.join(' > ');
  }

  function getGenericSelector(el) {
    // Returns a "fuzzy" selector good for batch selecting similar elements
    const tag = el.tagName.toLowerCase();
    if (el.classList.length > 0) {
      const classes = [...el.classList]
        .filter(c => !c.startsWith('__panda'))
        .map(c => CSS.escape(c))
        .join('.');
      if (classes) return `${tag}.${classes}`;
    }
    return tag;
  }

  function getXPath(el) {
    if (el.id) return `//*[@id="${el.id}"]`;
    const parts = [];
    let current = el;
    while (current && current.nodeType === Node.ELEMENT_NODE) {
      const tag = current.tagName.toLowerCase();
      const siblings = current.parentElement
        ? [...current.parentElement.children].filter(c => c.tagName === current.tagName)
        : [];
      const idx = siblings.length > 1 ? `[${siblings.indexOf(current) + 1}]` : '';
      parts.unshift(`${tag}${idx}`);
      current = current.parentElement;
    }
    return '/' + parts.join('/');
  }

  // ─── Element info ─────────────────────────────────────────────────────────
  function getElementInfo(el) {
    const attrs = {};
    for (const attr of el.attributes) {
      attrs[attr.name] = attr.value;
    }
    return {
      tag: el.tagName.toLowerCase(),
      text: el.innerText?.trim().slice(0, 500) ?? '',
      html: el.outerHTML.slice(0, 2000),
      cssSelector: getUniqueCssSelector(el),
      genericSelector: getGenericSelector(el),
      xpath: getXPath(el),
      attrs,
    };
  }

  function extractBySelector(selector, fields) {
    const elements = [...document.querySelectorAll(selector)];
    return elements.map(el => {
      const row = {};
      for (const f of fields) {
        if (f === 'text') row.text = el.innerText?.trim() ?? '';
        else if (f === 'html') row.html = el.outerHTML;
        else if (f === 'href') row.href = el.href ?? el.querySelector('a')?.href ?? '';
        else if (f === 'src') row.src = el.src ?? el.querySelector('img')?.src ?? '';
        else if (f.startsWith('@')) row[f] = el.getAttribute(f.slice(1)) ?? '';
        else row[f] = el.getAttribute(f) ?? '';
      }
      return row;
    });
  }

  // ─── Event listeners ──────────────────────────────────────────────────────
  function onMouseMove(e) {
    if (!inspectMode) return;
    const el = e.target;
    if (el === hoveredEl) return;
    if (hoveredEl && !selectedElements.includes(hoveredEl)) removeHover(hoveredEl);
    hoveredEl = el;
    if (!selectedElements.includes(el)) applyHover(el);
    const sel = getUniqueCssSelector(el);
    const count = document.querySelectorAll(getGenericSelector(el)).length;
    showOverlay(`${el.tagName.toLowerCase()}  ·  ${sel}  ·  ${count} similar`);
  }

  function onClick(e) {
    if (!inspectMode) return;
    e.preventDefault();
    e.stopPropagation();
    const el = e.target;
    const idx = selectedElements.indexOf(el);
    if (idx === -1) {
      selectedElements.push(el);
      removeHover(el);
      applySelect(el);
    } else {
      selectedElements.splice(idx, 1);
      removeSelect(el);
    }
    sendToPanel({
      type: 'SELECTION_UPDATED',
      elements: selectedElements.map(getElementInfo),
    });
  }

  function onKeyDown(e) {
    if (e.key === 'Escape' && inspectMode) {
      setInspectMode(false);
      sendToPanel({ type: 'INSPECT_MODE_CHANGED', active: false });
    }
  }

  function setInspectMode(active) {
    inspectMode = active;
    document.body.style.cursor = active ? 'crosshair' : '';
    if (!active) {
      if (hoveredEl && !selectedElements.includes(hoveredEl)) removeHover(hoveredEl);
      hoveredEl = null;
      hideOverlay();
    }
  }

  // ─── Communication with panel ─────────────────────────────────────────────
  function sendToPanel(payload) {
    chrome.runtime.sendMessage({ type: 'CONTENT_TO_PANEL', payload });
  }

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    switch (message.type) {
      case 'SET_INSPECT_MODE':
        setInspectMode(message.active);
        sendResponse({ ok: true });
        break;

      case 'CLEAR_SELECTION':
        selectedElements.forEach(removeSelect);
        selectedElements = [];
        sendResponse({ ok: true });
        break;

      case 'SELECT_BY_SELECTOR': {
        selectedElements.forEach(removeSelect);
        selectedElements = [];
        const matches = [...document.querySelectorAll(message.selector)];
        matches.forEach(el => {
          selectedElements.push(el);
          applySelect(el);
        });
        sendToPanel({
          type: 'SELECTION_UPDATED',
          elements: selectedElements.map(getElementInfo),
        });
        sendResponse({ count: matches.length });
        break;
      }

      case 'EXTRACT_DATA': {
        const data = extractBySelector(message.selector, message.fields);
        sendResponse({ data });
        break;
      }

      case 'GET_PAGE_INFO':
        sendResponse({
          url: location.href,
          title: document.title,
          elementCount: document.querySelectorAll('*').length,
        });
        break;

      case 'SCROLL_TO_ELEMENT': {
        const el = selectedElements[message.index];
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        sendResponse({ ok: true });
        break;
      }

      case 'HIGHLIGHT_SELECTOR': {
        // Temporarily flash elements matching a selector
        const els = [...document.querySelectorAll(message.selector)];
        els.forEach(el => {
          const orig = el.style.outline;
          el.style.outline = '2px solid #f59e0b';
          setTimeout(() => { el.style.outline = orig; }, 1200);
        });
        sendResponse({ count: els.length });
        break;
      }
    }
  });

  // Attach events
  document.addEventListener('mousemove', onMouseMove, true);
  document.addEventListener('click', onClick, true);
  document.addEventListener('keydown', onKeyDown, true);
})();
