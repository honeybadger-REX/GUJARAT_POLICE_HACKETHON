/* ==========================================================
   auth.js — shared by login.html, streaming.html, camera.html, vendor.html

   Usage (one tag per page, in <head>):
     <script src="auth.js" data-roles="admin,user"></script>   streaming
     <script src="auth.js" data-roles="admin"></script>        camera / vendor
   The page is guarded the moment this script loads: no session or the
   wrong role -> redirect before anything else runs.

   IMPORTANT: this only controls what the UI shows. Real enforcement
   has to happen in the backend (verify the token + role on every
   endpoint). Anyone can call the API directly, bypassing this file.
   ========================================================== */
const AUTH = (() => {
    const API_BASE = "http://127.0.0.1:8000/api";
    const SESSION_KEY = "gp_session";
    const LOGIN_PAGE = "login.html";
    const HOME_PAGE = "streaming.html";   // where everyone lands after login
    const VALID_ROLES = ["admin", "user"];

    let blocked = false;       // true once a redirect has been triggered
    let warned403 = false;     // show the "no permission" alert once, not per request

    // ---------- session ----------
    function getSession() {
        try {
            const s = JSON.parse(sessionStorage.getItem(SESSION_KEY));
            if (s && s.token && VALID_ROLES.includes(s.role)) return s;
        } catch (e) { /* corrupt entry -> treat as logged out */ }
        return null;
    }

    function isAdmin() {
        const s = getSession();
        return !!s && s.role === "admin";
    }

    function logout(message) {
        blocked = true;
        sessionStorage.removeItem(SESSION_KEY);
        const q = message ? "?msg=" + encodeURIComponent(message) : "";
        location.replace(LOGIN_PAGE + q);
    }

    // ---------- login (used by login.html) ----------
    // Expected backend response: { "token": "...", "role": "admin" | "user", "username": "..." }
    async function login(username, password) {
        let res, data;
        try {
            res = await fetch(API_BASE + "/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });
            data = await res.json().catch(() => ({}));
        } catch (e) {
            return { ok: false, message: "Cannot reach the server." };
        }

        const role = String(data.role || "").toLowerCase();
        if (!res.ok || !data.token || !VALID_ROLES.includes(role)) {
            const detail = typeof data.detail === "string" ? data.detail : data.message;
            return { ok: false, message: detail || "Invalid username or password." };
        }

        sessionStorage.setItem(SESSION_KEY, JSON.stringify({
            token: data.token,
            role: role,
            username: data.username || username
        }));
        return { ok: true };
    }

    // ---------- authenticated fetch ----------
    async function apiFetch(url, options = {}) {
        if (blocked) return new Promise(() => {});   // page is already redirecting; don't fire requests

        const session = getSession();
        const headers = Object.assign({}, options.headers || {});
        if (session) headers["Authorization"] = "Bearer " + session.token;

        const res = await fetch(url, Object.assign({}, options, { headers }));

        if (res.status === 401) {
            logout("Session expired. Please sign in again.");
            return new Promise(() => {});
        }
        if (res.status === 403 && !warned403) {
            warned403 = true;
            alert("You don't have permission to do that.");
        }
        return res;
    }

    // ---------- helpers ----------
    // Escape anything that came from the database before putting it in innerHTML.
    function esc(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    // rtsp://user:pass@host/x  ->  rtsp://•••@host/x   (display only)
    function maskUrl(url) {
        return String(url ?? "").replace(/^([a-z][a-z0-9+.-]*:\/\/)[^\/@]*@/i, "$1•••@");
    }

    // ---------- page guard ----------
    function guard() {
        const tag = document.currentScript;
        const allowed = ((tag && tag.dataset.roles) || "").split(",").map(r => r.trim()).filter(Boolean);
        if (allowed.length === 0) return;                 // login.html: no guard

        const session = getSession();
        if (!session) {
            blocked = true;
            location.replace(LOGIN_PAGE);
            return;
        }
        if (!allowed.includes(session.role)) {
            blocked = true;
            location.replace(HOME_PAGE);                  // logged in, but not allowed here
            return;
        }
        document.addEventListener("DOMContentLoaded", renderNav);
    }

    // ---------- nav bar ----------
    function renderNav() {
        const session = getSession();
        if (!session) return;

        const links = [{ href: "streaming.html", label: "Streaming" }];
        if (session.role === "admin") {
            links.push({ href: "camera.html", label: "Cameras" });
            links.push({ href: "vendor.html", label: "Vendors" });
        }

        const here = location.pathname.split("/").pop() || HOME_PAGE;

        const style = document.createElement("style");
        style.textContent = `
            #gp-nav { display:flex; align-items:center; justify-content:space-between; gap:16px;
                height:44px; flex-shrink:0; padding:0 20px; background:#0f131a;
                border-bottom:1px solid #262d3a; font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif; }
            #gp-nav .gp-links { display:flex; gap:4px; }
            #gp-nav a { color:#7d8899; text-decoration:none; font-size:13px; font-weight:600;
                padding:6px 12px; border-radius:6px; }
            #gp-nav a:hover { background:#171c25; color:#e6edf3; }
            #gp-nav a.active { background:#1c2530; color:#e6edf3; }
            #gp-nav .gp-user { display:flex; align-items:center; gap:10px; font-size:12px; color:#7d8899; }
            #gp-nav .gp-role { font-size:10px; font-weight:700; letter-spacing:0.06em; padding:2px 8px; border-radius:999px; }
            #gp-nav .gp-role.admin { background:#2a1f0d; color:#d29922; }
            #gp-nav .gp-role.user { background:#0f2238; color:#58a6ff; }
            #gp-nav button { background:#2b1213; color:#f85149; border:none; border-radius:6px;
                font-size:12px; font-weight:600; padding:6px 12px; cursor:pointer; }
            #gp-nav button:hover { opacity:0.85; }
        `;
        document.head.appendChild(style);

        const nav = document.createElement("nav");
        nav.id = "gp-nav";
        nav.innerHTML = `
            <div class="gp-links">
                ${links.map(l => `<a href="${l.href}" class="${l.href === here ? "active" : ""}">${l.label}</a>`).join("")}
            </div>
            <div class="gp-user">
                <span>${esc(session.username)}</span>
                <span class="gp-role ${esc(session.role)}">${esc(session.role.toUpperCase())}</span>
                <button type="button" id="gp-logout">Logout</button>
            </div>
        `;
        document.body.insertBefore(nav, document.body.firstChild);
        document.getElementById("gp-logout").addEventListener("click", () => logout());
    }

    guard();

    return { API_BASE, HOME_PAGE, getSession, isAdmin, login, logout, apiFetch, esc, maskUrl };
})();
