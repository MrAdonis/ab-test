```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Settings — Acacia</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #f8f8f7;
      --surface: #ffffff;
      --border: #e4e4e2;
      --border-strong: #c8c8c5;
      --text-primary: #1a1a18;
      --text-secondary: #6b6b68;
      --text-muted: #9b9b97;
      --accent: #2563eb;
      --accent-hover: #1d4ed8;
      --accent-subtle: #eff6ff;
      --danger: #dc2626;
      --danger-hover: #b91c1c;
      --danger-subtle: #fef2f2;
      --success-bg: #f0fdf4;
      --success-border: #bbf7d0;
      --success-text: #15803d;
      --error-bg: #fef2f2;
      --error-border: #fecaca;
      --error-text: #dc2626;
      --font: -apple-system, "SF Pro Text", "Segoe UI", "Helvetica Neue", sans-serif;
      --font-mono: "SF Mono", "Fira Code", "Cascadia Code", ui-monospace, monospace;
      --radius: 6px;
      --radius-sm: 4px;
    }

    body {
      font-family: var(--font);
      font-size: 13px;
      line-height: 1.5;
      color: var(--text-primary);
      background: var(--bg);
      min-height: 100vh;
    }

    /* ── Layout ── */
    .app-shell {
      display: grid;
      grid-template-columns: 220px 1fr;
      min-height: 100vh;
    }

    .sidebar {
      background: var(--surface);
      border-right: 1px solid var(--border);
      padding: 16px 0;
      position: sticky;
      top: 0;
      height: 100vh;
    }

    .sidebar-logo {
      padding: 0 16px 16px;
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      letter-spacing: -0.01em;
      border-bottom: 1px solid var(--border);
      margin-bottom: 8px;
    }

    .sidebar-section-label {
      padding: 12px 16px 4px;
      font-size: 11px;
      font-weight: 500;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .sidebar-nav a {
      display: block;
      padding: 6px 16px;
      font-size: 13px;
      color: var(--text-secondary);
      text-decoration: none;
      border-radius: 0;
      transition: background 100ms, color 100ms;
    }

    .sidebar-nav a:hover { background: var(--bg); color: var(--text-primary); }
    .sidebar-nav a.active {
      background: var(--accent-subtle);
      color: var(--accent);
      font-weight: 500;
    }

    .main {
      padding: 32px 40px;
      max-width: 680px;
    }

    /* ── Page header ── */
    .page-title {
      font-size: 20px;
      font-weight: 600;
      letter-spacing: -0.02em;
      margin-bottom: 4px;
    }

    .page-subtitle {
      font-size: 13px;
      color: var(--text-secondary);
      margin-bottom: 32px;
    }

    /* ── Section card ── */
    .section {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      margin-bottom: 20px;
      overflow: hidden;
    }

    .section-header {
      padding: 16px 20px;
      border-bottom: 1px solid var(--border);
    }

    .section-title {
      font-size: 13px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .section-desc {
      font-size: 12px;
      color: var(--text-secondary);
      margin-top: 2px;
    }

    .section-body { padding: 20px; }

    /* ── Form ── */
    .field { margin-bottom: 16px; }
    .field:last-child { margin-bottom: 0; }

    .field-label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 5px;
    }

    .field-helper {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .input {
      width: 100%;
      height: 32px;
      padding: 0 10px;
      font-family: var(--font);
      font-size: 13px;
      color: var(--text-primary);
      background: var(--surface);
      border: 1px solid var(--border-strong);
      border-radius: var(--radius-sm);
      outline: none;
      transition: border-color 120ms, box-shadow 120ms;
    }

    .input:hover { border-color: #a0a09c; }

    .input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
    }

    .input.error {
      border-color: var(--danger);
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.10);
    }

    .field-error {
      font-size: 11px;
      color: var(--danger);
      margin-top: 4px;
      display: none;
    }

    .field-error.visible { display: block; }

    /* ── Form footer ── */
    .form-footer {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 20px;
      padding-top: 16px;
      border-top: 1px solid var(--border);
    }

    /* ── Buttons ── */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      height: 30px;
      padding: 0 14px;
      font-family: var(--font);
      font-size: 12px;
      font-weight: 500;
      border-radius: var(--radius-sm);
      border: 1px solid transparent;
      cursor: pointer;
      text-decoration: none;
      transition: background 100ms, border-color 100ms, opacity 100ms, transform 80ms;
      white-space: nowrap;
      user-select: none;
    }

    .btn:active:not(:disabled) { transform: scale(0.98); }

    .btn-primary {
      background: var(--accent);
      color: #fff;
      border-color: var(--accent);
    }

    .btn-primary:hover:not(:disabled) { background: var(--accent-hover); border-color: var(--accent-hover); }
    .btn-primary:focus-visible {
      outline: none;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.30);
    }

    .btn-primary:disabled {
      opacity: 0.55;
      cursor: not-allowed;
    }

    .btn-secondary {
      background: var(--surface);
      color: var(--text-primary);
      border-color: var(--border-strong);
    }

    .btn-secondary:hover { background: var(--bg); }
    .btn-secondary:focus-visible {
      outline: none;
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    .btn-danger {
      background: var(--surface);
      color: var(--danger);
      border-color: #fca5a5;
    }

    .btn-danger:hover { background: var(--danger-subtle); border-color: var(--danger); }
    .btn-danger:focus-visible {
      outline: none;
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.20);
    }

    /* Spinner inside button */
    .btn-spinner {
      width: 12px;
      height: 12px;
      border: 1.5px solid rgba(255,255,255,0.35);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.65s linear infinite;
      display: none;
    }

    .btn.saving .btn-spinner { display: block; }
    .btn.saving .btn-label { opacity: 0.75; }

    @keyframes spin { to { transform: rotate(360deg); } }

    /* ── Toast ── */
    #toast-container {
      position: fixed;
      bottom: 20px;
      right: 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      z-index: 9999;
    }

    .toast {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 14px;
      border-radius: var(--radius);
      border: 1px solid;
      font-size: 13px;
      max-width: 360px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
      animation: toast-in 160ms ease-out;
    }

    @keyframes toast-in {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .toast.fade-out {
      animation: toast-out 200ms ease-in forwards;
    }

    @keyframes toast-out {
      from { opacity: 1; transform: translateY(0); }
      to   { opacity: 0; transform: translateY(4px); }
    }

    .toast-success {
      background: var(--success-bg);
      border-color: var(--success-border);
      color: var(--success-text);
    }

    .toast-error {
      background: var(--error-bg);
      border-color: var(--error-border);
      color: var(--error-text);
    }

    .toast-icon { font-size: 14px; flex-shrink: 0; }

    .toast-message { flex: 1; }

    .toast-close {
      background: none;
      border: none;
      cursor: pointer;
      color: inherit;
      opacity: 0.55;
      font-size: 14px;
      padding: 0 2px;
      line-height: 1;
      flex-shrink: 0;
    }

    .toast-close:hover { opacity: 1; }

    /* ── Danger zone ── */
    .danger-section {
      border-color: #fca5a5;
    }

    .danger-section .section-header {
      border-bottom-color: #fca5a5;
      background: var(--danger-subtle);
    }

    .danger-section .section-title { color: var(--danger); }

    .danger-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 24px;
      padding: 16px 20px;
    }

    .danger-row + .danger-row {
      border-top: 1px solid var(--border);
    }

    .danger-row-info strong {
      display: block;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 2px;
    }

    .danger-row-info p {
      font-size: 12px;
      color: var(--text-secondary);
      max-width: 380px;
    }

    .danger-row-action { flex-shrink: 0; padding-top: 1px; }

    /* ── Dialog ── */
    .dialog-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.30);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 8000;
    }

    .dialog-overlay.open { display: flex; }

    .dialog {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 24px;
      width: 400px;
      max-width: calc(100vw - 32px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 1px 4px rgba(0,0,0,0.06);
      animation: dialog-in 180ms ease-out;
    }

    @keyframes dialog-in {
      from { opacity: 0; transform: scale(0.97) translateY(-4px); }
      to   { opacity: 1; transform: scale(1) translateY(0); }
    }

    .dialog-title {
      font-size: 15px;
      font-weight: 600;
      margin-bottom: 8px;
      letter-spacing: -0.01em;
    }

    .dialog-body {
      font-size: 13px;
      color: var(--text-secondary);
      line-height: 1.6;
      margin-bottom: 20px;
    }

    .dialog-body strong { color: var(--text-primary); font-weight: 500; }

    .dialog-confirm-field { margin-bottom: 20px; }

    .dialog-confirm-label {
      font-size: 12px;
      color: var(--text-secondary);
      margin-bottom: 6px;
      display: block;
    }

    .dialog-confirm-label code {
      font-family: var(--font-mono);
      font-size: 11px;
      background: var(--bg);
      border: 1px solid var(--border);
      padding: 1px 5px;
      border-radius: 3px;
      color: var(--text-primary);
    }

    .dialog-actions {
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }

    .btn-danger-solid {
      background: var(--danger);
      color: #fff;
      border-color: var(--danger);
    }

    .btn-danger-solid:hover:not(:disabled) { background: var(--danger-hover); border-color: var(--danger-hover); }
    .btn-danger-solid:disabled { opacity: 0.45; cursor: not-allowed; }
    .btn-danger-solid:focus-visible {
      outline: none;
      box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.28);
    }

    /* ── Status text ── */
    .save-status {
      font-size: 12px;
      color: var(--text-muted);
      flex: 1;
    }

    @media (max-width: 640px) {
      .app-shell { grid-template-columns: 1fr; }
      .sidebar { display: none; }
      .main { padding: 20px 16px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
    }
  </style>
</head>
<body>
<div class="app-shell">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-logo">Acacia</div>
    <div class="sidebar-section-label">Account</div>
    <nav class="sidebar-nav">
      <a href="#" class="active">Profile</a>
      <a href="#">Security</a>
      <a href="#">Notifications</a>
      <a href="#">API Keys</a>
    </nav>
    <div class="sidebar-section-label">Workspace</div>
    <nav class="sidebar-nav">
      <a href="#">General</a>
      <a href="#">Members</a>
      <a href="#">Billing</a>
      <a href="#">Integrations</a>
    </nav>
  </aside>

  <!-- Main -->
  <main class="main">
    <h1 class="page-title">Profile</h1>
    <p class="page-subtitle">Update your display name and email address.</p>

    <!-- Profile form -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">Personal information</div>
        <div class="section-desc">Shown to teammates and in notifications.</div>
      </div>
      <div class="section-body">
        <form id="profile-form" novalidate>
          <div class="field">
            <label class="field-label" for="display-name">Display name</label>
            <input
              class="input"
              id="display-name"
              type="text"
              value="Marcus Chen"
              autocomplete="name"
              maxlength="64"
            >
            <div class="field-helper">Visible to all workspace members.</div>
            <div class="field-error" id="display-name-error"></div>
          </div>

          <div class="field">
            <label class="field-label" for="email">Email address</label>
            <input
              class="input"
              id="email"
              type="email"
              value="marcus@teamacacia.com"
              autocomplete="email"
            >
            <div class="field-helper">Used for login and account notifications.</div>
            <div class="field-error" id="email-error"></div>
          </div>

          <div class="form-footer">
            <button
              type="submit"
              class="btn btn-primary"
              id="save-btn"
            >
              <span class="btn-spinner" aria-hidden="true"></span>
              <span class="btn-label">Save changes</span>
            </button>
            <button type="button" class="btn btn-secondary" id="discard-btn">Discard</button>
            <span class="save-status" id="save-status" role="status" aria-live="polite"></span>
          </div>
        </form>
      </div>
    </div>

    <!-- Avatar section (static, no upload needed for demo) -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">Profile photo</div>
        <div class="section-desc">Your photo appears in comments, mentions, and the member list.</div>
      </div>
      <div class="section-body" style="display:flex;align-items:center;gap:16px;">
        <div style="width:48px;height:48px;border-radius:50%;background:#dbeafe;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:600;color:#2563eb;flex-shrink:0;border:1px solid #bfdbfe;">MC</div>
        <div>
          <button class="btn btn-secondary" style="margin-bottom:6px;">Upload photo</button>
          <div class="field-helper">JPEG or PNG, max 2 MB.</div>
        </div>
      </div>
    </div>

    <!-- Danger Zone -->
    <div class="section danger-section">
      <div class="section-header">
        <div class="section-title">Danger zone</div>
        <div class="section-desc">Actions here are permanent and cannot be undone.</div>
      </div>
      <div class="danger-row">
        <div class="danger-row-info">
          <strong>Delete account</strong>
          <p>Your account, all projects, and workspace data will be permanently deleted within 24 hours. This cannot be reversed.</p>
        </div>
        <div class="danger-row-action">
          <button class="btn btn-danger" id="delete-account-btn">Delete account</button>
        </div>
      </div>
    </div>
  </main>
</div>

<!-- Delete confirmation dialog -->
<div class="dialog-overlay" id="delete-dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
  <div class="dialog">
    <h2 class="dialog-title" id="dialog-title">Delete your account?</h2>
    <div class="dialog-body">
      <p>Your account (<strong>marcus@teamacacia.com</strong>) and all associated data will be permanently deleted. This action cannot be undone.</p>
    </div>
    <div class="dialog-confirm-field">
      <label class="dialog-confirm-label" for="confirm-input">
        Type <code>delete my account</code> to confirm
      </label>
      <input
        class="input"
        id="confirm-input"
        type="text"
        placeholder="delete my account"
        autocomplete="off"
      >
    </div>
    <div class="dialog-actions">
      <button class="btn btn-secondary" id="cancel-delete-btn">Cancel</button>
      <button class="btn btn-danger-solid" id="confirm-delete-btn" disabled>Delete account</button>
    </div>
  </div>
</div>

<!-- Toast container -->
<div id="toast-container" aria-live="assertive" aria-atomic="true"></div>

<script>
  /* ────────────────────────────────────────────
     Toast system
  ──────────────────────────────────────────── */
  function showToast(type, message, duration = 4000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
      <span class="toast-icon" aria-hidden="true">${type === 'success' ? '✓' : '✕'}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" aria-label="Dismiss">&times;</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    function dismiss() {
      toast.classList.add('fade-out');
      toast.addEventListener('animationend', () => toast.remove(), { once: true });
    }
    closeBtn.addEventListener('click', dismiss);

    container.appendChild(toast);
    setTimeout(dismiss, duration);
  }

  /* ────────────────────────────────────────────
     Profile form — save flow
  ──────────────────────────────────────────── */
  const form = document.getElementById('profile-form');
  const saveBtn = document.getElementById('save-btn');
  const saveStatus = document.getElementById('save-status');
  const nameInput = document.getElementById('display-name');
  const emailInput = document.getElementById('email');
  const nameError = document.getElementById('display-name-error');
  const emailError = document.getElementById('email-error');

  // Simulate failure roughly 30% of the time for demo variety
  let failNext = false;
  document.addEventListener('keydown', e => { if (e.key === 'f') failNext = !failNext; });

  function clearFieldErrors() {
    [nameInput, emailInput].forEach(el => el.classList.remove('error'));
    [nameError, emailError].forEach(el => { el.textContent = ''; el.classList.remove('visible'); });
  }

  function validateForm() {
    let valid = true;
    clearFieldErrors();

    if (!nameInput.value.trim()) {
      nameInput.classList.add('error');
      nameError.textContent = 'Display name is required.';
      nameError.classList.add('visible');
      nameInput.focus();
      valid = false;
    }

    const emailVal = emailInput.value.trim();
    if (!emailVal || !emailVal.includes('@')) {
      emailInput.classList.add('error');
      emailError.textContent = 'Enter a valid email address.';
      emailError.classList.add('visible');
      if (valid) emailInput.focus();
      valid = false;
    }

    return valid;
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    if (!validateForm()) return;

    // → Saving state
    saveBtn.disabled = true;
    saveBtn.classList.add('saving');
    const label = saveBtn.querySelector('.btn-label');
    label.textContent = 'Saving…';
    saveStatus.textContent = '';

    // Simulate network delay: 1.4 s
    const shouldFail = failNext;
    failNext = false;

    setTimeout(() => {
      saveBtn.classList.remove('saving');
      saveBtn.disabled = false;
      label.textContent = 'Save changes';

      if (shouldFail) {
        // Error path
        showToast('error', 'Profile not saved: network error. Check your connection and try again.');
        saveStatus.textContent = '';
      } else {
        // Success path
        showToast('success', 'Profile updated');
        saveStatus.textContent = 'Changes saved';
        setTimeout(() => { saveStatus.textContent = ''; }, 3000);
      }
    }, 1400);
  });

  document.getElementById('discard-btn').addEventListener('click', () => {
    clearFieldErrors();
    nameInput.value = 'Marcus Chen';
    emailInput.value = 'marcus@teamacacia.com';
    saveStatus.textContent = '';
  });

  /* ────────────────────────────────────────────
     Delete account dialog
  ──────────────────────────────────────────── */
  const deleteDialog = document.getElementById('delete-dialog');
  const confirmInput = document.getElementById('confirm-input');
  const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
  const CONFIRM_PHRASE = 'delete my account';

  function openDialog() {
    deleteDialog.classList.add('open');
    confirmInput.value = '';
    confirmDeleteBtn.disabled = true;
    setTimeout(() => confirmInput.focus(), 50);
  }

  function closeDialog() {
    deleteDialog.classList.remove('open');
    confirmInput.value = '';
    confirmDeleteBtn.disabled = true;
  }

  document.getElementById('delete-account-btn').addEventListener('click', openDialog);
  document.getElementById('cancel-delete-btn').addEventListener('click', closeDialog);

  // Close on overlay click
  deleteDialog.addEventListener('click', e => {
    if (e.target === deleteDialog) closeDialog();
  });

  // Close on Escape
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && deleteDialog.classList.contains('open')) closeDialog();
  });

  confirmInput.addEventListener('input', () => {
    confirmDeleteBtn.disabled = confirmInput.value.trim().toLowerCase() !== CONFIRM_PHRASE;
  });

  confirmDeleteBtn.addEventListener('click', () => {
    confirmDeleteBtn.disabled = true;
    confirmDeleteBtn.textContent = 'Deleting…';

    // Simulate async deletion (2 s)
    setTimeout(() => {
      closeDialog();
      showToast('success', 'Account deletion scheduled. You'll be signed out in 24 hours.', 6000);
    }, 2000);
  });
</script>
</body>
</html>
```

---

## UI String Inventory

### Buttons
| Context | Label |
|---------|-------|
| Profile form — idle | `Save changes` |
| Profile form — in-progress | `Saving…` |
| Profile form — secondary | `Discard` |
| Sidebar nav — static | `Profile`, `Security`, `Notifications`, `API Keys`, `General`, `Members`, `Billing`, `Integrations` |
| Avatar section | `Upload photo` |
| Danger zone row | `Delete account` |
| Dialog — cancel | `Cancel` |
| Dialog — confirm idle | `Delete account` |
| Dialog — confirm in-progress | `Deleting…` |

### Toast messages
| Trigger | Type | Message |
|---------|------|---------|
| Save success | success | `Profile updated` |
| Save error | error | `Profile not saved: network error. Check your connection and try again.` |
| Delete scheduled | success | `Account deletion scheduled. You'll be signed out in 24 hours.` |

### In-progress / status
| Location | String |
|----------|--------|
| Save button label (saving) | `Saving…` |
| Save status text (after success) | `Changes saved` |
| Dialog confirm button (deleting) | `Deleting…` |

### Form helpers
| Field | Helper text |
|-------|------------|
| Display name | `Visible to all workspace members.` |
| Email | `Used for login and account notifications.` |
| Avatar | `JPEG or PNG, max 2 MB.` |

### Inline field errors
| Field | Error |
|-------|-------|
| Display name (empty) | `Display name is required.` |
| Email (missing/invalid) | `Enter a valid email address.` |

### Dialog copy
| Element | String |
|---------|--------|
| Title | `Delete your account?` |
| Body | `Your account (marcus@teamacacia.com) and all associated data will be permanently deleted. This action cannot be undone.` |
| Confirm label | `Type delete my account to confirm` |

### Section descriptors
| Section | Title | Subtitle |
|---------|-------|---------|
| Page | `Profile` | `Update your display name and email address.` |
| Form card | `Personal information` | `Shown to teammates and in notifications.` |
| Avatar card | `Profile photo` | `Your photo appears in comments, mentions, and the member list.` |
| Danger zone | `Danger zone` | `Actions here are permanent and cannot be undone.` |
| Danger row | `Delete account` | `Your account, all projects, and workspace data will be permanently deleted within 24 hours. This cannot be reversed.` |
