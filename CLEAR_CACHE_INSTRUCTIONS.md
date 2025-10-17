# Clear Browser Cache Instructions

## The Problem
When you click "Upload Documents", you're seeing the old green UI instead of the modern UI because your browser has cached the old HTML page.

## Solution: Clear Browser Cache

### Option 1: Hard Refresh (Recommended - Quick)
1. Open the page showing the old UI: `http://localhost:5000/load_documents/e63b06cf-163d-4fc5-98f8-c40ae8cae89a`
2. Press one of these key combinations:
   - **Windows/Linux**: `Ctrl + Shift + R` or `Ctrl + F5`
   - **Mac**: `Cmd + Shift + R`
3. The page should reload with the new modern UI

### Option 2: Clear Cache via DevTools
1. Open Developer Tools:
   - **Windows/Linux**: Press `F12` or `Ctrl + Shift + I`
   - **Mac**: `Cmd + Option + I`
2. Go to the **Network** tab
3. Check the box that says **"Disable cache"**
4. Keep DevTools open and refresh the page with `F5`

### Option 3: Clear All Cached Data (Most Thorough)
1. Open your browser settings
2. Find "Clear browsing data" or "Clear cache"
3. Select:
   - ✅ Cached images and files
   - ✅ Time range: Last hour (or All time)
4. Click "Clear data"
5. Refresh the page

### Option 4: Use Incognito/Private Mode (For Testing)
1. Open a new Incognito/Private window:
   - **Chrome**: `Ctrl + Shift + N`
   - **Firefox**: `Ctrl + Shift + P`
   - **Edge**: `Ctrl + Shift + N`
2. Navigate to: `http://localhost:5000`
3. Login and test the Upload Documents page

## Also Check: Restart Flask Server
If clearing cache doesn't work, restart your Flask server:

```bash
# Stop the current server (Ctrl + C in the terminal where it's running)
# Then restart it:
cd d:/GITHUB-REPOS/chatminds/chatminds
python app.py
```

## What You Should See After Clearing Cache
- ✅ Modern gradient header with blue/purple colors
- ✅ Drag-and-drop file upload area
- ✅ Three cards: Upload Files, Load from URL, Crawl Website
- ✅ File type badges (PDF, TXT, DOC/DOCX)
- ✅ Clean, modern design with icons
- ✅ Footer at the bottom with social links

## What You Should NOT See
- ❌ Green background with "ASK-AI" header
- ❌ Simple "Choose files" button
- ❌ Old-style "Upload Documents" card
- ❌ Green navigation buttons

---

**Note**: The templates have been fully modernized. The old UI only appears due to browser caching.
