```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Settings — Vanta</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #f9f9f8;
      --surface:   #ffffff;
      --border:    #e4e4e1;
      --border-focus: #8b8b85;
      --text-primary:   #1a1a17;
      --text-secondary: #6b6b64;
      --text-muted:     #a8a89f;
      --accent:    #1a1a17;
      --accent-hover: #3a3a35;
      --danger:    #c0392b;
      --danger-bg: #fff5f4;
      --danger-border: #f5c6c2;
      --success-bg: #f0faf4;
      --success-border: #b2dfcc;
      --success-text: #1a6b3c;
      --error-bg: #fff5f4;
      --error-border: #f5c6c2;
      --error-text: #c0392b;
      --radius-sm: 6px;
      --radius-md: 8px;
      --shadow-sm: 0 1px 3px rgba(26,26,23,0.06), 0 1px 2px rgba(26,26,23,0.04);
      --shadow-focus: 0 0 0 3px rgba(26,26,23,0.10);
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
      font-size: 14px;
      line-height: 1.5;
      color: var(--text-primary);
      background: var(--bg);
      min-height: 100vh;
    }

    /* ── Layout ────────────────────────────────────── */
    .layout {
      display: grid;
      grid-template-columns: 220px 1fr;
      min-height: 100vh;
      max-width: 1100px;
      margin: 0 auto;
    }

    /* ── Sidebar ───────────────────────────────────── */
    .sidebar {
      border-right: 1px solid var(--border);
      padding: 32px 0;
      background: var(--surface);
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
    }

    .sidebar-brand {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 20px 24px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 16px;
    }

    .sidebar-brand-mark {
      width: 24px;
      height: 24px;
      background: var(--text-primary);
      border-radius: 5px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }

    .sidebar-brand-mark svg { display: block; }

    .sidebar-brand-name {
      font-size: 14px;
      font-weight: 600;
      letter-spacing: -0.01em;
      color: var(--text-primary);
    }

    .sidebar-section-label {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      padding: 0 20px;
      margin-bottom: 4px;
      margin-top: 16px;
    }

    .sidebar-nav a {
      display: block;
      padding: 7px 20px;
      font-size: 13.5px;
      color: var(--text-secondary);
      text-decoration: none;
      border-radius: 0;
      transition: color 120ms ease-out, background 120ms ease-out;
    }

    .sidebar-nav a:hover { color: var(--text-primary); background: rgba(26,26,23,0.04); }
    .sidebar-nav a.active { color: var(--text-primary); font-weight: 500; background: rgba(26,26,23,0.06); }
    .sidebar-nav a:focus-visible { outline: none; box-shadow: inset 0 0 0 2px var(--border-focus); }

    /* ── Main content ──────────────────────────────── */
    .main {
      padding: 40px 48px;
      max-width: 680px;
    }

    .page-header {
      margin-bottom: 32px;
    }

    .page-title {
      font-size: 20px;
      font-weight: 600;
      letter-spacing: -0.02em;
      color: var(--text-primary);
      margin-bottom: 4px;
    }

    .page-subtitle {
      font-size: 13.5px;
      color: var(--text-secondary);
    }

    /* ── Section card ──────────────────────────────── */
    .section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }

    .section-header {
      padding: 20px 24px 0;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }

    .section-title {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .section-desc {
      font-size: 12.5px;
      color: var(--text-secondary);
      margin-top: 2px;
    }

    .section-body {
      padding: 0 24px 24px;
    }

    /* ── Form fields ───────────────────────────────── */
    .field {
      margin-bottom: 16px;
    }

    .field:last-of-type { margin-bottom: 0; }

    .field label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 6px;
    }

    .field-hint {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 4px;
    }

    .input {
      width: 100%;
      height: 36px;
      padding: 0 12px;
      font-size: 13.5px;
      font-family: inherit;
      color: var(--text-primary);
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      outline: none;
      transition: border-color 120ms ease-out, box-shadow 120ms ease-out;
    }

    .input:hover { border-color: var(--border-focus); }
    .input:focus { border-color: var(--border-focus); box-shadow: var(--shadow-focus); }
    .input::placeholder { color: var(--text-muted); }
    .input:disabled {
      background: var(--bg);
      color: var(--text-muted);
      cursor: not-allowed;
    }
    .input.input-error { border-color: var(--danger); box-shadow: 0 0 0 3px rgba(192,57,43,0.10); }

    /* ── Form row (actions) ────────────────────────── */
    .form-actions {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 20px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
    }

    /* ── Buttons ───────────────────────────────────── */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      height: 34px;
      padding: 0 14px;
      font-size: 13.5px;
      font-family: inherit;
      font-weight: 500;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      transition: background 120ms ease-out, opacity 120ms ease-out, transform 80ms ease-out;
      user-select: none;
      white-space: nowrap;
    }

    .btn:active:not(:disabled) { transform: scale(0.98); }
    .btn:focus-visible { outline: none; box-shadow: var(--shadow-focus); }

    .btn-primary {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
    }
    .btn-primary:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }

    .btn-secondary {
      background: transparent;
      color: var(--text-secondary);
      border-color: var(--border);
    }
    .btn-secondary:hover:not(:disabled) { background: rgba(26,26,23,0.04); color: var(--text-primary); }

    .btn-danger {
      background: transparent;
      color: var(--danger);
      border-color: var(--danger-border);
    }
    .btn-danger:hover:not(:disabled) { background: var(--danger-bg); }

    .btn:disabled {
      opacity: 0.45;
      cursor: not-allowed;
    }

    /* Loading spinner inline */
    .btn-spinner {
      width: 14px;
      height: 14px;
      border: 2px solid rgba(255,255,255,0.35);
      border-top-color: #ffffff;
      border-radius: 50%;
      animation: spin 0.65s linear infinite;
      display: none;
    }
    .btn-spinner.secondary {
      border-color: rgba(26,26,23,0.15);
      border-top-color: var(--text-secondary);
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .btn.loading .btn-spinner { display: block; }
    .btn.loading .btn-label { opacity: 0.7; }

    /* ── Toast ─────────────────────────────────────── */
    #toast-region {
      position: fixed;
      bottom: 24px;
      right: 24px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 100;
      pointer-events: none;
    }

    .toast {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      padding: 12px 16px;
      border-radius: var(--radius-md);
      border: 1px solid;
      font-size: 13px;
      max-width: 340px;
      pointer-events: auto;
      box-shadow: 0 4px 12px rgba(26,26,23,0.10);
      animation: toast-in 200ms ease-out;
    }

    .toast.success {
      background: var(--success-bg);
      border-color: var(--success-border);
      color: var(--success-text);
    }

    .toast.error {
      background: var(--error-bg);
      border-color: var(--error-border);
      color: var(--error-text);
    }

    .toast-icon { flex-shrink: 0; margin-top: 1px; }

    .toast-body { flex: 1; }
    .toast-title { font-weight: 600; font-size: 13px; }
    .toast-desc { font-size: 12.5px; margin-top: 1px; opacity: 0.85; }

    .toast-dismiss {
      background: none;
      border: none;
      cursor: pointer;
      color: currentColor;
      opacity: 0.55;
      padding: 0;
      flex-shrink: 0;
      font-size: 16px;
      line-height: 1;
      transition: opacity 100ms;
    }
    .toast-dismiss:hover { opacity: 1; }
    .toast-dismiss:focus-visible { outline: 2px solid currentColor; border-radius: 3px; }

    .toast.removing {
      animation: toast-out 160ms ease-in forwards;
    }

    @keyframes toast-in {
      from { opacity: 0; transform: translateY(8px) scale(0.97); }
      to   { opacity: 1; transform: translateY(0)   scale(1); }
    }
    @keyframes toast-out {
      from { opacity: 1; transform: translateY(0)  scale(1); }
      to   { opacity: 0; transform: translateY(4px) scale(0.97); }
    }

    /* ── Danger zone ───────────────────────────────── */
    .section.danger {
      border-color: var(--danger-border);
    }

    .section-header.danger {
      background: var(--danger-bg);
      border-bottom-color: var(--danger-border);
      border-radius: var(--radius-md) var(--radius-md) 0 0;
    }

    .section-title.danger { color: var(--danger); }

    .danger-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }

    .danger-row-text {}
    .danger-row-label { font-size: 13.5px; font-weight: 500; color: var(--text-primary); }
    .danger-row-desc { font-size: 12.5px; color: var(--text-secondary); margin-top: 2px; }

    /* ── Confirm dialog overlay ─────────────────────── */
    .overlay {
      position: fixed;
      inset: 0;
      background: rgba(26,26,23,0.45);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 200;
      padding: 24px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 180ms ease-out;
    }

    .overlay.open {
      opacity: 1;
      pointer-events: auto;
    }

    .dialog {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      box-shadow: 0 16px 48px rgba(26,26,23,0.18);
      width: 100%;
      max-width: 440px;
      padding: 28px;
      transform: scale(0.96) translateY(6px);
      transition: transform 200ms ease-out;
    }

    .overlay.open .dialog {
      transform: scale(1) translateY(0);
    }

    .dialog-title {
      font-size: 16px;
      font-weight: 600;
      letter-spacing: -0.015em;
      color: var(--text-primary);
      margin-bottom: 8px;
    }

    .dialog-body {
      font-size: 13.5px;
      color: var(--text-secondary);
      line-height: 1.55;
      margin-bottom: 20px;
    }

    .dialog-body strong { color: var(--text-primary); font-weight: 500; }

    .dialog-confirm-field {
      margin-bottom: 20px;
    }

    .dialog-confirm-field label {
      display: block;
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 6px;
    }

    .dialog-confirm-field .confirm-hint {
      font-size: 12.5px;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }

    .dialog-confirm-field .confirm-hint code {
      font-family: "SF Mono", "Fira Mono", monospace;
      background: rgba(26,26,23,0.07);
      padding: 1px 5px;
      border-radius: 3px;
      font-size: 12px;
      color: var(--text-primary);
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    /* ── Inline field error ─────────────────────────── */
    .field-error {
      font-size: 12px;
      color: var(--danger);
      margin-top: 4px;
      display: none;
    }
    .field-error.visible { display: block; }

    /* ── Avatar placeholder ─────────────────────────── */
    .avatar-row {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 20px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: #e2e0db;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      font-weight: 600;
      color: var(--text-secondary);
      flex-shrink: 0;
      user-select: none;
    }

    .avatar-info {}
    .avatar-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
    .avatar-email { font-size: 12.5px; color: var(--text-secondary); margin-top: 1px; }

    /* ── Save status indicator ──────────────────────── */
    .save-status {
      font-size: 12.5px;
      color: var(--text-secondary);
      display: none;
      align-items: center;
      gap: 6px;
    }
    .save-status.visible { display: flex; }
    .save-status-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      flex-shrink: 0;
    }
    .save-status.saving .save-status-dot {
      background: #d4a827;
      animation: pulse 1s ease-in-out infinite;
    }
    .save-status.saved .save-status-dot { background: #2a7d4f; }
    .save-status.failed .save-status-dot { background: var(--danger); }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    /* ── Responsive ─────────────────────────────────── */
    @media (max-width: 720px) {
      .layout { grid-template-columns: 1fr; }
      .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); padding: 16px 0; }
      .main { padding: 24px 20px; }
      .danger-row { flex-direction: column; align-items: flex-start; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
    }
  </style>
</head>
<body>

<div class="layout">
  <!-- Sidebar -->
  <nav class="sidebar" aria-label="Settings navigation">
    <div class="sidebar-brand">
      <div class="sidebar-brand-mark">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <rect x="2" y="2" width="4" height="4" fill="white"/>
          <rect x="8" y="2" width="4" height="4" fill="white" opacity=".6"/>
          <rect x="2" y="8" width="4" height="4" fill="white" opacity=".6"/>
          <rect x="8" y="8" width="4" height="4" fill="white" opacity=".3"/>
        </svg>
      </div>
      <span class="sidebar-brand-name">Vanta</span>
    </div>
    <p class="sidebar-section-label">Account</p>
    <div class="sidebar-nav">
      <a href="#" class="active" aria-current="page">Profile</a>
      <a href="#">Notifications</a>
      <a href="#">Security</a>
      <a href="#">Billing</a>
    </div>
    <p class="sidebar-section-label">Workspace</p>
    <div class="sidebar-nav">
      <a href="#">Members</a>
      <a href="#">Integrations</a>
      <a href="#">API keys</a>
    </div>
  </nav>

  <!-- Main -->
  <main class="main">
    <div class="page-header">
      <h1 class="page-title">Profile</h1>
      <p class="page-subtitle">Manage your personal details and preferences.</p>
    </div>

    <!-- Profile form -->
    <section class="section" aria-label="Profile information">
      <div class="section-header">
        <p class="section-title">Personal information</p>
        <p class="section-desc">Visible to teammates and in notifications.</p>
      </div>
      <div class="section-body">

        <!-- Avatar row -->
        <div class="avatar-row">
          <div class="avatar" aria-hidden="true">AJ</div>
          <div class="avatar-info">
            <div class="avatar-name">Alex Johnson</div>
            <div class="avatar-email">alex@acme.io</div>
          </div>
        </div>

        <form id="profile-form" novalidate>
          <div class="field">
            <label for="display-name">Display name</label>
            <input
              class="input"
              type="text"
              id="display-name"
              name="display-name"
              value="Alex Johnson"
              autocomplete="name"
              aria-describedby="display-name-hint display-name-error"
            />
            <p class="field-hint" id="display-name-hint">Shown in comments, assignments, and emails.</p>
            <p class="field-error" id="display-name-error" role="alert" aria-live="polite"></p>
          </div>

          <div class="field">
            <label for="email">Email address</label>
            <input
              class="input"
              type="email"
              id="email"
              name="email"
              value="alex@acme.io"
              autocomplete="email"
              aria-describedby="email-hint email-error"
            />
            <p class="field-hint" id="email-hint">Used for sign-in and transactional emails.</p>
            <p class="field-error" id="email-error" role="alert" aria-live="polite"></p>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn btn-primary" id="save-btn" aria-label="Save profile changes">
              <span class="btn-spinner" aria-hidden="true"></span>
              <span class="btn-label">Save changes</span>
            </button>
            <button type="button" class="btn btn-secondary" id="discard-btn">Discard</button>
            <div class="save-status" id="save-status" aria-live="polite" aria-atomic="true">
              <span class="save-status-dot" aria-hidden="true"></span>
              <span class="save-status-text"></span>
            </div>
          </div>
        </form>

      </div>
    </section>

    <!-- Danger zone -->
    <section class="section danger" aria-label="Danger zone">
      <div class="section-header danger">
        <p class="section-title danger">Danger zone</p>
        <p class="section-desc">These actions are permanent and cannot be undone.</p>
      </div>
      <div class="section-body">
        <div class="danger-row">
          <div class="danger-row-text">
            <p class="danger-row-label">Delete account</p>
            <p class="danger-row-desc">Permanently removes your account, all projects, and data.</p>
          </div>
          <button
            class="btn btn-danger"
            id="delete-account-btn"
            aria-haspopup="dialog"
          >
            Delete account
          </button>
        </div>
      </div>
    </section>

  </main>
</div>

<!-- Toast region -->
<div id="toast-region" aria-live="assertive" aria-atomic="false" role="region" aria-label="Notifications"></div>

<!-- Delete confirm dialog -->
<div class="overlay" id="delete-overlay" role="dialog" aria-modal="true" aria-labelledby="dialog-title" aria-describedby="dialog-desc">
  <div class="dialog">
    <h2 class="dialog-title" id="dialog-title">Delete your account?</h2>
    <p class="dialog-body" id="dialog-desc">
      This will immediately and <strong>permanently</strong> delete your account,
      all workspaces you own, and every project, file, and API key within them.
      Members of those workspaces will lose access. <strong>This cannot be undone.</strong>
    </p>
    <div class="dialog-confirm-field">
      <label for="confirm-input">To confirm, type <code>delete my account</code> below</label>
      <input
        class="input"
        type="text"
        id="confirm-input"
        autocomplete="off"
        autocorrect="off"
        autocapitalize="off"
        spellcheck="false"
        placeholder="delete my account"
        aria-describedby="confirm-field-error"
      />
      <p class="field-error" id="confirm-field-error" role="alert" aria-live="polite"></p>
    </div>
    <div class="dialog-actions">
      <button class="btn btn-secondary" id="cancel-delete-btn">Cancel</button>
      <button class="btn btn-danger" id="confirm-delete-btn" disabled aria-disabled="true">
        <span class="btn-spinner secondary" aria-hidden="true"></span>
        <span class="btn-label">Yes, delete my account</span>
      </button>
    </div>
  </div>
</div>

<script>
(function () {
  // ── Utils ──────────────────────────────────────────
  function showToast(type, title, desc) {
    const region = document.getElementById('toast-region');
    const icons = {
      success: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="7" stroke="#2a7d4f" stroke-width="1.5"/><path d="M5 8.5l2 2 4-4" stroke="#2a7d4f" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
      error: `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="7" stroke="#c0392b" stroke-width="1.5"/><path d="M8 5v4M8 11v.5" stroke="#c0392b" stroke-width="1.5" stroke-linecap="round"/></svg>`
    };

    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.setAttribute('role', 'status');
    el.innerHTML = `
      <span class="toast-icon">${icons[type]}</span>
      <div class="toast-body">
        <div class="toast-title">${title}</div>
        ${desc ? `<div class="toast-desc">${desc}</div>` : ''}
      </div>
      <button class="toast-dismiss" aria-label="Dismiss notification">×</button>
    `;

    const dismiss = el.querySelector('.toast-dismiss');
    dismiss.addEventListener('click', () => removeToast(el));
    region.appendChild(el);

    // Auto-dismiss after 4s
    setTimeout(() => removeToast(el), 4000);
    return el;
  }

  function removeToast(el) {
    if (!el.parentNode) return;
    el.classList.add('removing');
    el.addEventListener('animationend', () => el.remove(), { once: true });
  }

  function setSaveStatus(state, text) {
    const el = document.getElementById('save-status');
    el.className = `save-status ${state} ${state ? 'visible' : ''}`;
    el.querySelector('.save-status-text').textContent = text;
  }

  // ── Profile form ───────────────────────────────────
  const form        = document.getElementById('profile-form');
  const saveBtn     = document.getElementById('save-btn');
  const discardBtn  = document.getElementById('discard-btn');
  const nameInput   = document.getElementById('display-name');
  const emailInput  = document.getElementById('email');
  const nameError   = document.getElementById('display-name-error');
  const emailError  = document.getElementById('email-error');

  const originalValues = {
    name:  nameInput.value,
    email: emailInput.value
  };

  function validateField(input, errorEl, rules) {
    for (const { test, message } of rules) {
      if (!test(input.value.trim())) {
        input.classList.add('input-error');
        errorEl.textContent = message;
        errorEl.classList.add('visible');
        return false;
      }
    }
    input.classList.remove('input-error');
    errorEl.classList.remove('visible');
    return true;
  }

  function validateForm() {
    const nameValid = validateField(nameInput, nameError, [
      { test: v => v.length > 0, message: 'Display name is required.' },
      { test: v => v.length >= 2, message: 'Name must be at least 2 characters.' }
    ]);
    const emailValid = validateField(emailInput, emailError, [
      { test: v => v.length > 0, message: 'Email address is required.' },
      { test: v => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), message: 'Enter a valid email address.' }
    ]);
    return nameValid && emailValid;
  }

  // Clear errors on input
  [nameInput, emailInput].forEach(input => {
    input.addEventListener('input', () => {
      input.classList.remove('input-error');
      const errEl = input.id === 'display-name' ? nameError : emailError;
      errEl.classList.remove('visible');
      setSaveStatus('', '');
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    // Disable form
    nameInput.disabled = true;
    emailInput.disabled = true;
    saveBtn.disabled = true;
    discardBtn.disabled = true;
    saveBtn.classList.add('loading');
    setSaveStatus('saving', 'Saving…');

    // Simulate network: 70% success, 30% error (for demo variety)
    const succeed = Math.random() > 0.3;
    await new Promise(r => setTimeout(r, 1400));

    saveBtn.classList.remove('loading');
    nameInput.disabled = false;
    emailInput.disabled = false;
    saveBtn.disabled = false;
    discardBtn.disabled = false;

    if (succeed) {
      setSaveStatus('saved', 'Saved');
      showToast('success', 'Profile updated', 'Your changes have been saved.');
      originalValues.name  = nameInput.value;
      originalValues.email = emailInput.value;
    } else {
      setSaveStatus('failed', 'Save failed');
      showToast('error', 'Could not save changes', 'Check your connection and try again.');
    }

    // Clear status after 4s
    setTimeout(() => setSaveStatus('', ''), 4200);
  });

  discardBtn.addEventListener('click', () => {
    nameInput.value  = originalValues.name;
    emailInput.value = originalValues.email;
    nameInput.classList.remove('input-error');
    emailInput.classList.remove('input-error');
    nameError.classList.remove('visible');
    emailError.classList.remove('visible');
    setSaveStatus('', '');
  });

  // ── Delete account dialog ──────────────────────────
  const overlay         = document.getElementById('delete-overlay');
  const openBtn         = document.getElementById('delete-account-btn');
  const cancelBtn       = document.getElementById('cancel-delete-btn');
  const confirmBtn      = document.getElementById('confirm-delete-btn');
  const confirmInput    = document.getElementById('confirm-input');
  const confirmError    = document.getElementById('confirm-field-error');
  const CONFIRM_PHRASE  = 'delete my account';

  function openDialog() {
    overlay.classList.add('open');
    confirmInput.value = '';
    confirmBtn.disabled = true;
    confirmBtn.setAttribute('aria-disabled', 'true');
    confirmError.classList.remove('visible');
    // Focus the confirm input after transition
    setTimeout(() => confirmInput.focus(), 210);
    document.addEventListener('keydown', handleDialogKey);
  }

  function closeDialog() {
    overlay.classList.remove('open');
    document.removeEventListener('keydown', handleDialogKey);
    openBtn.focus();
  }

  function handleDialogKey(e) {
    if (e.key === 'Escape') closeDialog();
    // Trap focus within dialog
    if (e.key === 'Tab') {
      const focusable = overlay.querySelectorAll('button:not([disabled]), input:not([disabled])');
      const first = focusable[0];
      const last  = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  }

  openBtn.addEventListener('click', openDialog);
  cancelBtn.addEventListener('click', closeDialog);

  // Close on backdrop click
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeDialog(); });

  // Enable confirm button when phrase matches
  confirmInput.addEventListener('input', () => {
    const match = confirmInput.value.trim() === CONFIRM_PHRASE;
    confirmBtn.disabled = !match;
    confirmBtn.setAttribute('aria-disabled', String(!match));
    confirmError.classList.remove('visible');
  });

  confirmBtn.addEventListener('click', async () => {
    if (confirmInput.value.trim() !== CONFIRM_PHRASE) {
      confirmError.textContent = `Type exactly: "${CONFIRM_PHRASE}"`;
      confirmError.classList.add('visible');
      return;
    }

    // Lock UI
    confirmBtn.classList.add('loading');
    confirmBtn.disabled = true;
    cancelBtn.disabled  = true;
    confirmInput.disabled = true;

    await new Promise(r => setTimeout(r, 1800));

    // In a real app this would redirect; for demo show error toast + reset
    confirmBtn.classList.remove('loading');
    cancelBtn.disabled  = false;
    confirmInput.disabled = false;
    closeDialog();

    showToast('error', 'Deletion failed', 'An unexpected error occurred. Contact support if this persists.');
  });
})();
</script>
</body>
</html>
```

---

## UI String Inventory

### Buttons
| Element | Label |
|---|---|
| Primary save | `Save changes` |
| Discard edits | `Discard` |
| Open delete dialog | `Delete account` |
| Dialog cancel | `Cancel` |
| Dialog confirm (destructive) | `Yes, delete my account` |

### In-progress states
| Context | String |
|---|---|
| Save button (loading) | spinner + `Save changes` (label stays, spinner appears) |
| Save status dot | `Saving…` |
| Confirm delete button (loading) | spinner + `Yes, delete my account` |

### Success states
| Context | String |
|---|---|
| Save status dot | `Saved` |
| Toast title | `Profile updated` |
| Toast description | `Your changes have been saved.` |

### Error states
| Context | String |
|---|---|
| Save status dot | `Save failed` |
| Toast title (save failure) | `Could not save changes` |
| Toast description (save failure) | `Check your connection and try again.` |
| Toast title (delete failure) | `Deletion failed` |
| Toast description (delete failure) | `An unexpected error occurred. Contact support if this persists.` |
| Display name required | `Display name is required.` |
| Display name too short | `Name must be at least 2 characters.` |
| Invalid email | `Enter a valid email address.` |
| Email required | `Email address is required.` |
| Confirm phrase mismatch | `Type exactly: "delete my account"` |

### Helper / hint strings
| Element | String |
|---|---|
| Display name hint | `Shown in comments, assignments, and emails.` |
| Email hint | `Used for sign-in and transactional emails.` |
| Section subtitle (profile) | `Visible to teammates and in notifications.` |
| Section subtitle (danger) | `These actions are permanent and cannot be undone.` |
| Danger row label | `Delete account` |
| Danger row description | `Permanently removes your account, all projects, and data.` |
| Confirm phrase label | `To confirm, type delete my account below` |
| Confirm input placeholder | `delete my account` |

### Dialog body
| Element | String |
|---|---|
| Dialog title | `Delete your account?` |
| Dialog body | `This will immediately and permanently delete your account, all workspaces you own, and every project, file, and API key within them. Members of those workspaces will lose access. This cannot be undone.` |

### Navigation labels
| Element | String |
|---|---|
| Page title | `Profile` |
| Page subtitle | `Manage your personal details and preferences.` |
| Section title | `Personal information` |
| Section title (danger) | `Danger zone` |
| Sidebar nav items | `Profile`, `Notifications`, `Security`, `Billing`, `Members`, `Integrations`, `API keys` |

### Accessibility-only labels
| Element | String |
|---|---|
| Save button `aria-label` | `Save profile changes` |
| Toast dismiss `aria-label` | `Dismiss notification` |
| `aria-label` on settings nav | `Settings navigation` |
| `aria-label` on toast region | `Notifications` |
