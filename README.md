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
2. **Firestore Database**: create it (production mode, europe region). It stores
   the invite allowlist (`config/access`) and user profiles (`users/{uid}`).
3. **Firestore rules**: publish `firestore.rules` from this repo (Firestore >
   Rules > paste > Publish). They enforce admin-only writes to the allowlist.
4. **First admin**: `federico.gennari@jakala.com` is a bootstrap admin
   (see `BOOTSTRAP_ADMINS` in `index.html`); they can sign up directly and are
   auto-promoted to **admin**.

### How new users are activated (same model as the Quotation Hub)
- An **admin** opens the **Utenti** tab and enters the person's `@jakala.com`
  email, choosing the role (Member / Admin). This adds them to the access list.
- The admin shares the app link. The invited person clicks **Create account**
  and sets their own password. Only invited emails (or bootstrap admins) can
  register; everyone else is blocked.
- After first login the person appears in the **Utenti** table, where admins can
  change their role or disable their access.

### Recommended
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
