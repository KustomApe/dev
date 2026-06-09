# 🐼 Panda Scraper

A Chrome extension for point-and-click HTML element scraping. Inspect any web page, select elements visually, define extraction rules, and export data as JSON or CSV — no code required.

---

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** using the toggle in the top-right corner
3. Click **Load unpacked**
4. Select the `panda_scraper` folder
5. The Panda Scraper icon will appear in your Chrome toolbar

> **Note:** The extension requires Chrome 114 or later for Side Panel support.

---

## Interface Overview

Click the 🐼 icon in your toolbar to open the **Side Panel**. The panel has three tabs:

| Tab | Purpose |
|---|---|
| **Inspector** | Select elements on the page visually |
| **Rules** | Define named extraction rules |
| **Data** | Run rules and export results |

---

## How to Use

### 1. Inspect & Select Elements

1. Open the side panel and go to the **Inspector** tab
2. Click the **Inspect** button — your cursor changes to a crosshair
3. Hover over the page — elements highlight in purple as you move
4. The tooltip at the bottom of the page shows the element's tag, CSS selector, and how many similar elements exist
5. **Click an element** to select it (highlighted in green)
6. Click more elements to add them to your selection
7. Press **Esc** or click **Stop** to exit inspect mode

### 2. Work with the Selector

After selecting an element, the **CSS Selector** and **XPath** fields populate automatically.

- **Edit the selector** manually and press **Enter** or click **Apply** to reselect based on your custom selector
- Click **Flash** to blink all matching elements on the page (amber highlight) — useful to confirm scope
- Click **Select Similar** to automatically select all elements on the page that match the same tag + class pattern

### 3. Review Selected Elements

Each selected element appears as a card in the Inspector tab:

- The card shows the element's **tag** and a **text preview**
- Click the card to expand it and see:
  - The unique **CSS selector**
  - The **XPath**
  - All **HTML attributes** (href, src, class, data-* etc.)
- Click **⊙** to scroll the page to that element
- Click **✕** to remove an element from the selection

### 4. Create Extraction Rules

Rules define *what* to extract from a selector and are saved for reuse across sessions.

1. Go to the **Rules** tab
2. Click **+ Add Rule**
3. Fill in:
   - **Name** — a label for the rule (e.g. "Product titles")
   - **CSS Selector** — which elements to target (e.g. `.product-card h2`)
   - **Extract fields** — check any combination of:
     - `text` — visible inner text
     - `html` — raw outer HTML
     - `href` — link URL (or first `<a>` inside the element)
     - `src` — image/media source (or first `<img>` inside)
     - `id` — the `id` attribute
     - `class` — the `class` attribute
   - **Custom attribute** — any attribute using `@` prefix, e.g. `@data-price`, `@aria-label`
4. Click **Save Rule**

**Tip:** Click **Save Template** in the Inspector tab to pre-fill a new rule from your current selection.

### 5. Run Rules & Preview Data

1. Go to the **Data** tab
2. Click **▶ Run All Rules** to extract data from all saved rules against the current page
3. Results appear as tables — one per rule — showing the number of rows found and all extracted fields
4. You can also run a single rule from the **Rules** tab by clicking its **▶** button

### 6. Export Data

From the **Data** tab:

| Button | Output |
|---|---|
| **Export JSON** | Downloads a `.json` file with all results grouped by rule name |
| **Export CSV** | Downloads a `.csv` file with each rule as a labeled section |
| **Copy** | Copies the full JSON to your clipboard |

---

## Tips & Tricks

- **Repeating elements** (product listings, search results, table rows) work best — use **Select Similar** to grab all instances at once
- The **Flash** button is your friend before running a rule — always confirm your selector matches what you expect
- Rules are **persistent** across browser sessions; they are stored in `chrome.storage.local`
- For sites with dynamic content (infinite scroll, lazy loading), scroll the page to load more elements before running a rule
- Use **custom attributes** like `@data-id` or `@data-price` to extract structured metadata that isn't visible as text
- The XPath field is read-only and useful if you need to paste the selector into other tools (Playwright, Puppeteer, etc.)

---

## File Structure

```
panda_scraper/
├── manifest.json       # Extension config (Manifest V3)
├── background.js       # Service worker — opens side panel, relays messages
├── content.js          # Injected into pages — handles hover, selection, extraction
├── panel.html          # Side panel markup
├── panel.js            # Side panel logic (Inspector / Rules / Data)
├── panel.css           # Dark-theme UI styles
└── icons/
    ├── icon16.png
    ├── icon32.png
    ├── icon48.png
    └── icon128.png
```

---

## Permissions Used

| Permission | Reason |
|---|---|
| `activeTab` | Access the current tab to inject the content script |
| `scripting` | Execute the content script on demand |
| `storage` | Persist saved rules across sessions |
| `sidePanel` | Display the panel UI alongside the page |
| `downloads` | Save exported JSON/CSV files |
| `<all_urls>` | Allow scraping on any website |

---

## Limitations

- Does not work on `chrome://` or `chrome-extension://` pages
- Cannot scrape content inside `<iframe>` elements from a different origin
- Dynamic content loaded after page interaction (e.g. click-to-reveal) must be triggered manually before running a rule
- The extension does not perform pagination or automated crawling across multiple pages

---

## License

MIT
