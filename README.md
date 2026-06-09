# SEO Staffing Hub

Internal command center for the JAKALA SEO &amp; GEO team: project staffing,
team effort/utilization, allocation matrix and assisted assignment.

Single-file static app (`index.html`, vanilla JS) backed by Firebase.

## Stack
- **Frontend**: single `index.html`, vanilla JS, no build step
- **Auth**: Firebase Authentication, email/password, restricted to `@jakala.com`
  (identical model to the SEO Quotation Hub)
- **Data**: Firebase Realtime Database (`staffing/v1`)
- **User profiles**: Firestore `users/{uid}` (role, displayName, active)
- **Hosting**: Cloudflare (static assets via `wrangler.jsonc`)

## Firebase project
`seo-staffing-hub` (europe-west1). Config is inline in `index.html` (public by
design; security is enforced by Auth + DB rules, not by hiding the key).

### Required setup (one-time, in the Firebase console)
1. **Authentication > Sign-in method**: enable **Email/Password**.
2. Create the first account by signing up in the app with an `@jakala.com`
   email. `federico.gennari@jakala.com` is auto-promoted to **admin**
   (see `BOOTSTRAP_ADMINS` in `index.html`).

### Optional / recommended
- **Firestore**: enable Cloud Firestore so user profiles persist. If Firestore
  is not enabled, login still works (profile load fails gracefully).
- **Realtime Database rules**: now that real auth is in place, tighten the rules
  to require authentication:
  ```json
  { "rules": { "staffing": { ".read": "auth != null", ".write": "auth != null" } } }
  ```

## Local preview
No Node required. From this folder:
```
python -m http.server 4173
```
Then open http://localhost:4173

## Build
`index.html` is regenerated from `_original.html` (the recovered Netlify build)
by `build.py`, which applies the JAKALA palette and the Quotation-Hub auth
model. Edit `build.py` and re-run `python build.py` to regenerate, or edit
`index.html` directly.

## Deploy (Cloudflare)
See the deployment guide. The app is pure static; `wrangler.jsonc` serves the
folder with SPA fallback, mirroring the SEO Quotation Hub setup.
