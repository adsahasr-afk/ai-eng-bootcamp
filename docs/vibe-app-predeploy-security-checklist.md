# Pre-Deploy Security Checklist for Vibe-Coded Apps

**Use before deploying any AI-generated app (Lovable, Bolt, v0, Replit, Cursor, etc.) to any hosting portal — including "private" preview links.**

Core mental model:
- The browser is **untrusted**. Anything the client can reach without a server-side check is effectively public.
- An obscure or "private" URL is **not** an access control. Assume every preview link will leak.
- AI generators optimize for "it works," not "it's locked down." Every item below must be verified by you, not assumed.

Scoring: aim to answer **YES** (or N/A) to every item before deploy. Any NO is a blocker.

---

## 1. Access control (the wall in front of the app)

- [ ] There is a **real authentication wall** enforced server-side (Supabase Auth, Clerk, Auth0, etc.) — not a JavaScript `if (loggedIn)` conditional.
- [ ] Unauthenticated users see **no data** — not the UI-hidden version, actually no data returned from the API.
- [ ] Authorization is checked **server-side** on every privileged operation (reads, writes, admin actions), not just in the UI.
- [ ] Tested: hit a protected endpoint directly (curl / DevTools) with no session — it returns 401/403, not data.

## 2. Database — Row Level Security (the #1 cause of these breaches)

- [ ] **RLS is enabled on every table** (Supabase or equivalent). Default posture is **deny-all**.
- [ ] Explicit policies scope every row to its owner (e.g. `auth.uid() = user_id`).
- [ ] Tested: query each table using **only the public/anon key** and confirm you get nothing you shouldn't.
- [ ] No table is left "temporarily open" for debugging. (These become permanent.)

## 3. Secrets — nothing sensitive in the client bundle

- [ ] Opened DevTools → **Network** and **Sources**, and listed every key/token in the shipped bundle.
- [ ] Only **truly-public** keys are present (Supabase anon *with RLS on*, Stripe publishable key). Confirmed each is safe-to-be-public.
- [ ] **No** service-role keys, DB connection strings, private API keys, JWT secrets, or webhook signing secrets in front-end code.
- [ ] Privileged secrets live server-side only (Edge Functions / serverless / env vars).
- [ ] **Rotated** any secret that has ever been committed to git or shipped to a browser.

## 4. Server-side logic

- [ ] Operations that must be trusted (writes, admin reads, payments, emails) run behind an endpoint that **re-checks identity and authorization** on the server.
- [ ] Input is validated/sanitized server-side (no trusting client-supplied IDs, roles, prices, or flags).
- [ ] No mass-assignment: the client cannot set fields like `is_admin`, `role`, or `user_id` directly.

## 5. Preview / staging hygiene (treat as PUBLIC)

- [ ] Preview and staging environments contain **synthetic/anonymized data only** — no real names, emails, phone numbers, or PII.
- [ ] `noindex` / `robots.txt` set so crawlers don't surface the preview URL.
- [ ] Assumed the URL will leak (screenshots, referrers, community feeds) and confirmed nothing sensitive is exposed even if it does.
- [ ] Preview environments are torn down / rotated when no longer needed.

## 6. Data leakage vectors

- [ ] `Referrer-Policy: no-referrer` (or `same-origin`) set, so the app URL isn't handed to third-party APIs, fonts, analytics, or image hosts.
- [ ] Reviewed all third-party calls the app makes — none receive secrets or PII in query strings or headers.
- [ ] CORS is scoped to known origins, not `*`, for any authenticated API.
- [ ] Error responses don't leak stack traces, table names, or internal details to the client.

## 7. Transport & headers

- [ ] HTTPS enforced everywhere; no mixed content.
- [ ] Security headers present where the platform allows: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Strict-Transport-Security`.
- [ ] Cookies (if used) are `HttpOnly`, `Secure`, and `SameSite`.

## 8. Abuse & rate limiting

- [ ] Auth endpoints and expensive/data-returning endpoints have **rate limiting**.
- [ ] Any AI/LLM call proxied through your backend has usage caps (protects against cost-drain and key abuse).
- [ ] File uploads (if any) validate type/size and are stored with restricted access.

## 9. Final verification pass (do this every deploy)

- [ ] **Bundle audit:** open DevTools, list every secret visible — confirm all are safe-to-be-public.
- [ ] **Anon-key test:** attempt to read every table with only the public key — confirm deny.
- [ ] **No-auth test:** hit protected endpoints with no session — confirm 401/403.
- [ ] **Leaked-link test:** open the preview URL in a clean/incognito browser with no login — confirm no sensitive data is reachable.
- [ ] Re-run this pass **after any AI regeneration** — generators frequently reintroduce disabled RLS or re-embed secrets.

---

### The one-line summary
A "private" hosting link is public-by-URL. Breaches happen because AI-generated front-ends embed keys and skip Row Level Security, so anyone with the leaked link queries the database directly. Defense = server-enforced auth + RLS default-deny + zero privileged secrets in the client + treat previews as public with synthetic data.
