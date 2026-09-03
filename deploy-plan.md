# Deploy Plan: Android-Only Offline PWA

## What I recommend

Use a **static HTTPS host + minimal PWA wrapper**:

1. Keep `index.html` as the app entrypoint.
2. Add a `manifest.webmanifest` so Android Chrome can install it.
3. Add a `service-worker.js` that pre-caches `index.html` (and icons).
4. Host it on a simple static platform (Cloudflare Pages, Netlify, or GitHub Pages).
5. Open the URL on your Android phone once, install to home screen, then it works offline.

For your use-case (only you, Android-only, offline access), this is the lowest-friction approach.

---

## Why this is the best fit for your goals

### 1) Android installation requires web-app signals
Android "install" behavior in Chrome expects:
- HTTPS
- A web manifest
- A service worker

Without these, you can still open the page in browser, but install behavior is less reliable or unavailable.

### 2) Offline access needs a service worker cache
Even if the file is small, offline mode on Android works consistently when a service worker stores the app shell (`index.html` and related assets) in Cache Storage.

### 3) Your app structure is ideal for this
Your `index.html` already embeds timetable JSON directly, so offline is straightforward:
- No API dependency
- No dynamic backend
- No auth/session complexity

### 4) Single-user scope means optimize for simplicity
Since this is only for you:
- No need for a server backend
- No need for multi-user auth
- No need for complex deployment pipelines

---

## Suggested implementation details

### A) Add a web manifest
Create `manifest.webmanifest` with:
- `name`: "Harringay Departures"
- `short_name`: "Departures"
- `start_url`: `/index.html`
- `display`: `standalone`
- `background_color`: match current theme
- `theme_color`: match current theme
- `icons`: at least `192x192` and `512x512` PNG

And in `index.html`, add:
```html
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#0d1117">
```

### B) Add a service worker
Create `service-worker.js` that:
- On install: caches `/index.html`, `/manifest.webmanifest`, icons
- On fetch: serves cache first for these app shell files
- Falls back to network when needed

Register it in `index.html`:
```html
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js');
  });
}
</script>
```

### C) Versioning updates
When timetable content changes, bump a cache version constant in `service-worker.js` (for example `timetable-v3`) so old cached files are cleaned and replaced.

---

## Deployment options (ranked for your case)

### Option 1 (Recommended): Cloudflare Pages
**Why:** dead-simple static deploy, free HTTPS, fast global caching, minimal maintenance.

### Option 2: Netlify
**Why:** equally easy static hosting and HTTPS; great if you prefer Netlify UI.

### Option 3: GitHub Pages
**Why:** good if this repo is already in GitHub.
**Caveat:** project pages use `/repo-name/` path, so `start_url` and asset paths must account for subpath hosting.

---

## Alternatives and trade-offs

### Alternative A: Local file only (`file://`) without deployment
- **Pro:** zero hosting.
- **Con:** installability is poor/inconsistent; service workers do not work as expected on `file://`; updates are manual file copies.
- **Verdict:** not recommended if you want a real installable PWA experience.

### Alternative B: Run local server on phone (Termux) and self-host
- **Pro:** fully local and private, no external hosting.
- **Con:** setup and ongoing upkeep are more technical; service must stay configured correctly.
- **Verdict:** viable for advanced users, but higher friction than static hosting.

### Alternative C: Build a native Android wrapper (WebView/TWA)
- **Pro:** app-store style packaging, tighter OS integration.
- **Con:** much more build/release complexity for little benefit in your single-user case.
- **Verdict:** overkill unless you later need native features.

---

## Privacy and access for "only me"

Because this is static content, private login is optional unless the data is sensitive.

If you want to limit casual access:
- Use a hard-to-guess URL.
- Or protect the site with Cloudflare Access / Netlify password gate.

For your current timetable app, the simplest secure-enough setup is usually public static hosting + offline install on your phone.

---

## Practical install flow on Android

1. Deploy the site over HTTPS.
2. Open it in Chrome on Android.
3. Wait a few seconds for service worker install.
4. Tap `Install app` / `Add to Home screen`.
5. Turn on airplane mode and launch from home screen to verify offline behavior.

---

## Final recommendation

Implement a minimal PWA (`manifest + service worker`) and deploy to Cloudflare Pages.

It gives you exactly what you asked for:
- installable on Android,
- opens like an app,
- works offline,
- minimal ongoing maintenance,
- no unnecessary backend complexity for a single personal user.
