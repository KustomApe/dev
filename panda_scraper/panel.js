// ─── State ────────────────────────────────────────────────────────────────────
let inspectActive = false;
let selectedElements = [];   // [{tag, text, cssSelector, genericSelector, xpath, attrs, html}]
let rules = [];              // [{id, name, selector, fields}]
let extractedData = {};      // {ruleId: [{...row}]}
let editingRuleId = null;

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadRules();
  setupTabs();
  setupInspector();
  setupRules();
  setupData();
  loadPageInfo();

  // Listen for messages from content script (relayed via background)
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg._from !== 'content') return;
    if (msg.type === 'SELECTION_UPDATED') onSelectionUpdated(msg.elements);
    if (msg.type === 'INSPECT_MODE_CHANGED') onInspectModeChanged(msg.active);
  });
});

// ─── Utilities ────────────────────────────────────────────────────────────────
function sendToContent(payload) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: 'PANEL_TO_CONTENT', payload }, resolve);
  });
}

async function getActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
}

function uuid() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2);
}

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── Page info ─────────────────────────────────────────────────────────────────
async function loadPageInfo() {
  const res = await sendToContent({ type: 'GET_PAGE_INFO' });
  if (res?.url) {
    const url = new URL(res.url);
    document.getElementById('pageInfo').textContent = url.hostname;
    document.getElementById('pageInfo').title = res.url;
  }
}

// ─── Tabs ─────────────────────────────────────────────────────────────────────
function setupTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
  });
}

// ─── Inspector ────────────────────────────────────────────────────────────────
function setupInspector() {
  const btnInspect = document.getElementById('btnInspect');
  const btnClear = document.getElementById('btnClear');
  const btnSelectAll = document.getElementById('btnSelectAll');
  const btnApply = document.getElementById('btnApplySelector');
  const btnHighlight = document.getElementById('btnHighlight');
  const selectorInput = document.getElementById('selectorInput');

  btnInspect.addEventListener('click', toggleInspect);
  btnClear.addEventListener('click', clearSelection);
  btnSelectAll.addEventListener('click', selectSimilar);
  btnApply.addEventListener('click', applyManualSelector);
  btnHighlight.addEventListener('click', flashSelector);

  selectorInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') applyManualSelector();
  });
}

async function toggleInspect() {
  inspectActive = !inspectActive;
  const btn = document.getElementById('btnInspect');
  btn.classList.toggle('active', inspectActive);
  btn.textContent = inspectActive ? '⏹ Stop' : '🔍 Inspect';
  await sendToContent({ type: 'SET_INSPECT_MODE', active: inspectActive });
}

function onInspectModeChanged(active) {
  inspectActive = active;
  const btn = document.getElementById('btnInspect');
  btn.classList.toggle('active', active);
  btn.innerHTML = active
    ? '⏹ Stop'
    : `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg> Inspect`;
}

function onSelectionUpdated(elements) {
  selectedElements = elements;
  renderElementList();
  updateSelectorBar();
}

function updateSelectorBar() {
  const bar = document.getElementById('selectorBar');
  const header = document.getElementById('selectionHeader');
  const countEl = document.getElementById('selectionCount');
  const empty = document.getElementById('emptyState');

  if (selectedElements.length === 0) {
    bar.style.display = 'none';
    header.style.display = 'none';
    empty.style.display = 'flex';
    return;
  }

  bar.style.display = 'block';
  header.style.display = 'block';
  empty.style.display = 'none';
  countEl.textContent = `${selectedElements.length} element${selectedElements.length > 1 ? 's' : ''} selected`;

  const first = selectedElements[0];
  document.getElementById('selectorInput').value = first.genericSelector;
  document.getElementById('xpathInput').value = first.xpath;

  updateSelectorMeta(first.genericSelector);
}

async function updateSelectorMeta(selector) {
  if (!selector) return;
  try {
    const res = await sendToContent({ type: 'HIGHLIGHT_SELECTOR', selector });
    document.getElementById('selectorMeta').textContent =
      res ? `${res.count} element${res.count !== 1 ? 's' : ''} on page` : '';
  } catch {}
}

async function applyManualSelector() {
  const selector = document.getElementById('selectorInput').value.trim();
  if (!selector) return;
  try {
    await sendToContent({ type: 'SELECT_BY_SELECTOR', selector });
    updateSelectorMeta(selector);
  } catch (e) {
    document.getElementById('selectorMeta').textContent = 'Invalid selector';
  }
}

async function flashSelector() {
  const selector = document.getElementById('selectorInput').value.trim();
  if (!selector) return;
  const res = await sendToContent({ type: 'HIGHLIGHT_SELECTOR', selector });
  document.getElementById('selectorMeta').textContent =
    res ? `Flashed ${res.count} element${res.count !== 1 ? 's' : ''}` : '';
}

async function clearSelection() {
  await sendToContent({ type: 'CLEAR_SELECTION' });
  selectedElements = [];
  renderElementList();
  updateSelectorBar();
}

async function selectSimilar() {
  if (!selectedElements.length) return;
  const selector = document.getElementById('selectorInput').value.trim()
    || selectedElements[0].genericSelector;
  await sendToContent({ type: 'SELECT_BY_SELECTOR', selector });
}

function renderElementList() {
  const list = document.getElementById('elementList');
  list.innerHTML = '';

  selectedElements.forEach((el, idx) => {
    const card = document.createElement('div');
    card.className = 'el-card';
    card.innerHTML = `
      <div class="el-card-header" data-idx="${idx}">
        <span class="el-tag">&lt;${escapeHtml(el.tag)}&gt;</span>
        <span class="el-text-preview">${escapeHtml(el.text.slice(0, 80) || '(no text)')}</span>
        <div class="el-actions">
          <button class="icon-btn btn-scroll" title="Scroll to element" data-idx="${idx}">⊙</button>
          <button class="icon-btn btn-remove" title="Remove from selection" data-idx="${idx}">✕</button>
        </div>
      </div>
      <div class="el-card-body" id="elBody${idx}">
        <div class="detail-row">
          <label>CSS Selector</label>
          <code>${escapeHtml(el.cssSelector)}</code>
        </div>
        <div class="detail-row">
          <label>XPath</label>
          <code>${escapeHtml(el.xpath)}</code>
        </div>
        ${Object.keys(el.attrs).length ? `
        <table class="attr-table">
          ${Object.entries(el.attrs).map(([k, v]) => `
            <tr><td>${escapeHtml(k)}</td><td>${escapeHtml(v)}</td></tr>
          `).join('')}
        </table>` : ''}
      </div>
    `;
    list.appendChild(card);
  });

  // Toggle expand
  list.querySelectorAll('.el-card-header').forEach(header => {
    header.addEventListener('click', (e) => {
      if (e.target.closest('.el-actions')) return;
      const idx = header.dataset.idx;
      document.getElementById(`elBody${idx}`).classList.toggle('open');
    });
  });

  // Scroll to element
  list.querySelectorAll('.btn-scroll').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      await sendToContent({ type: 'SCROLL_TO_ELEMENT', index: parseInt(btn.dataset.idx) });
    });
  });

  // Remove element
  list.querySelectorAll('.btn-remove').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.idx);
      selectedElements.splice(idx, 1);
      renderElementList();
      updateSelectorBar();
      // Re-sync content script selection
      if (selectedElements.length > 0) {
        await sendToContent({
          type: 'SELECT_BY_SELECTOR',
          selector: selectedElements.map(el => el.cssSelector).join(', '),
        });
      } else {
        await sendToContent({ type: 'CLEAR_SELECTION' });
      }
    });
  });
}

// ─── Rules ────────────────────────────────────────────────────────────────────
function loadRules() {
  chrome.storage.local.get('pandaRules', (res) => {
    rules = res.pandaRules || [];
    renderRules();
  });
}

function saveRules() {
  chrome.storage.local.set({ pandaRules: rules });
}

function setupRules() {
  document.getElementById('btnAddRule').addEventListener('click', () => openRuleEditor(null));
  document.getElementById('btnSaveTemplate').addEventListener('click', saveCurrentAsRule);
  document.getElementById('btnRuleCancel').addEventListener('click', closeRuleEditor);
  document.getElementById('btnRuleSave').addEventListener('click', saveRule);
}

function renderRules() {
  const list = document.getElementById('rulesList');
  const empty = document.getElementById('rulesEmpty');
  list.innerHTML = '';

  if (rules.length === 0) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  rules.forEach(rule => {
    const card = document.createElement('div');
    card.className = 'rule-card';
    card.innerHTML = `
      <div class="rule-card-info">
        <div class="rule-card-name">${escapeHtml(rule.name)}</div>
        <div class="rule-card-selector">${escapeHtml(rule.selector)}</div>
        <div class="rule-card-fields">
          ${rule.fields.map(f => `<span class="field-chip">${escapeHtml(f)}</span>`).join('')}
        </div>
      </div>
      <div class="rule-card-actions">
        <button class="icon-btn btn-run-rule" data-id="${rule.id}" title="Run this rule">▶</button>
        <button class="icon-btn btn-edit-rule" data-id="${rule.id}" title="Edit">✎</button>
        <button class="icon-btn btn-delete-rule" data-id="${rule.id}" title="Delete">✕</button>
      </div>
    `;
    list.appendChild(card);
  });

  list.querySelectorAll('.btn-run-rule').forEach(btn => {
    btn.addEventListener('click', () => runRule(btn.dataset.id));
  });
  list.querySelectorAll('.btn-edit-rule').forEach(btn => {
    btn.addEventListener('click', () => openRuleEditor(btn.dataset.id));
  });
  list.querySelectorAll('.btn-delete-rule').forEach(btn => {
    btn.addEventListener('click', () => deleteRule(btn.dataset.id));
  });
}

function openRuleEditor(id) {
  editingRuleId = id;
  const editor = document.getElementById('ruleEditor');
  const title = document.getElementById('ruleEditorTitle');
  const nameInput = document.getElementById('ruleName');
  const selectorInput = document.getElementById('ruleSelector');
  const checkboxes = editor.querySelectorAll('.fields-grid input[type=checkbox]');
  const customAttr = document.getElementById('ruleCustomAttr');

  if (id) {
    const rule = rules.find(r => r.id === id);
    title.textContent = 'Edit Rule';
    nameInput.value = rule.name;
    selectorInput.value = rule.selector;
    checkboxes.forEach(cb => { cb.checked = rule.fields.includes(cb.value); });
    const customFields = rule.fields.filter(f => !['text','html','href','src','@id','@class'].includes(f));
    customAttr.value = customFields.join(', ');
  } else {
    title.textContent = 'New Rule';
    nameInput.value = '';
    selectorInput.value = selectedElements[0]?.genericSelector ?? '';
    checkboxes.forEach(cb => { cb.checked = cb.value === 'text'; });
    customAttr.value = '';
  }

  editor.style.display = 'block';
  document.getElementById('rulesList').style.display = 'none';
  document.getElementById('btnAddRule').style.display = 'none';
  document.getElementById('btnSaveTemplate').style.display = 'none';
  document.getElementById('rulesEmpty').style.display = 'none';
}

function closeRuleEditor() {
  document.getElementById('ruleEditor').style.display = 'none';
  document.getElementById('rulesList').style.display = 'block';
  document.getElementById('btnAddRule').style.display = '';
  document.getElementById('btnSaveTemplate').style.display = '';
  renderRules();
  editingRuleId = null;
}

function saveRule() {
  const editor = document.getElementById('ruleEditor');
  const name = document.getElementById('ruleName').value.trim();
  const selector = document.getElementById('ruleSelector').value.trim();
  if (!name || !selector) return;

  const checkboxFields = [...editor.querySelectorAll('.fields-grid input[type=checkbox]')]
    .filter(cb => cb.checked).map(cb => cb.value);
  const customVal = document.getElementById('ruleCustomAttr').value.trim();
  const customFields = customVal ? customVal.split(',').map(s => s.trim()).filter(Boolean) : [];
  const fields = [...checkboxFields, ...customFields];

  if (editingRuleId) {
    const rule = rules.find(r => r.id === editingRuleId);
    Object.assign(rule, { name, selector, fields });
  } else {
    rules.push({ id: uuid(), name, selector, fields });
  }

  saveRules();
  closeRuleEditor();
}

function deleteRule(id) {
  rules = rules.filter(r => r.id !== id);
  saveRules();
  renderRules();
}

function saveCurrentAsRule() {
  if (!selectedElements.length) return;
  openRuleEditor(null);
  document.getElementById('ruleName').value = `Rule ${rules.length + 1}`;
  document.getElementById('ruleSelector').value = document.getElementById('selectorInput').value || selectedElements[0].genericSelector;
}

async function runRule(id) {
  const rule = rules.find(r => r.id === id);
  if (!rule) return;
  const res = await sendToContent({ type: 'EXTRACT_DATA', selector: rule.selector, fields: rule.fields });
  if (res) {
    extractedData[id] = res.data;
    switchToDataTab();
    renderData();
  }
}

// ─── Data ─────────────────────────────────────────────────────────────────────
function setupData() {
  document.getElementById('btnRunAll').addEventListener('click', runAllRules);
  document.getElementById('btnExportJSON').addEventListener('click', exportJSON);
  document.getElementById('btnExportCSV').addEventListener('click', exportCSV);
  document.getElementById('btnCopyData').addEventListener('click', copyData);
}

async function runAllRules() {
  for (const rule of rules) {
    const res = await sendToContent({ type: 'EXTRACT_DATA', selector: rule.selector, fields: rule.fields });
    if (res) extractedData[rule.id] = res.data;
  }
  renderData();
}

function renderData() {
  const container = document.getElementById('dataResults');
  const empty = document.getElementById('dataEmpty');
  container.innerHTML = '';

  const entries = Object.entries(extractedData).filter(([, rows]) => rows?.length > 0);
  if (entries.length === 0) {
    empty.style.display = 'flex';
    return;
  }
  empty.style.display = 'none';

  for (const [ruleId, rows] of entries) {
    const rule = rules.find(r => r.id === ruleId);
    const block = document.createElement('div');
    block.className = 'result-block';

    const cols = rows.length > 0 ? Object.keys(rows[0]) : [];

    block.innerHTML = `
      <div class="result-block-header">
        <span class="result-block-name">${escapeHtml(rule?.name ?? ruleId)}</span>
        <span class="result-count">${rows.length} rows</span>
      </div>
      <div class="data-table-wrap">
        <table class="data-table">
          <thead>
            <tr>${cols.map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${rows.map(row =>
              `<tr>${cols.map(c => `<td title="${escapeHtml(row[c])}">${escapeHtml(String(row[c] ?? '').slice(0, 120))}</td>`).join('')}</tr>`
            ).join('')}
          </tbody>
        </table>
      </div>
    `;
    container.appendChild(block);
  }
}

function getAllRows() {
  const result = {};
  for (const [ruleId, rows] of Object.entries(extractedData)) {
    const rule = rules.find(r => r.id === ruleId);
    result[rule?.name ?? ruleId] = rows;
  }
  return result;
}

async function exportJSON() {
  const data = getAllRows();
  const json = JSON.stringify(data, null, 2);
  downloadFile(json, `panda-scraper-${Date.now()}.json`, 'application/json');
}

async function exportCSV() {
  const data = getAllRows();
  const sections = [];
  for (const [name, rows] of Object.entries(data)) {
    if (!rows?.length) continue;
    const cols = Object.keys(rows[0]);
    const header = cols.map(c => `"${c}"`).join(',');
    const body = rows.map(row =>
      cols.map(c => `"${String(row[c] ?? '').replace(/"/g, '""')}"`).join(',')
    );
    sections.push(`# ${name}\n${header}\n${body.join('\n')}`);
  }
  downloadFile(sections.join('\n\n'), `panda-scraper-${Date.now()}.csv`, 'text/csv');
}

async function copyData() {
  const data = getAllRows();
  const text = JSON.stringify(data, null, 2);
  await navigator.clipboard.writeText(text);
}

function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  chrome.downloads.download({ url, filename, saveAs: true });
}

function switchToDataTab() {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector('[data-tab="data"]').classList.add('active');
  document.getElementById('tab-data').classList.add('active');
}
