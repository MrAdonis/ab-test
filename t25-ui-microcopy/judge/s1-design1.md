```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>团队成员管理</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #f8f9fa;
    --surface: #ffffff;
    --border: #e2e5e9;
    --border-muted: #eef0f3;
    --text-primary: #111318;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;
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
    --shadow-sm: 0 1px 2px rgba(17,19,24,0.06);
    --shadow-md: 0 4px 12px rgba(17,19,24,0.10);
    --radius: 6px;
    --radius-lg: 8px;
  }

  body {
    font-family: -apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
    font-size: 13px;
    line-height: 1.4;
    color: var(--text-primary);
    background: var(--bg);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }

  /* Layout */
  .layout {
    max-width: 900px;
    margin: 0 auto;
    padding: 32px 24px;
  }

  /* Page header */
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  .page-header-left h1 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
  }

  .page-header-left p {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 2px;
  }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0 14px;
    height: 32px;
    font-size: 13px;
    font-weight: 500;
    border-radius: var(--radius);
    border: 1px solid transparent;
    cursor: pointer;
    transition: background 120ms, border-color 120ms, color 120ms, opacity 120ms;
    white-space: nowrap;
    text-decoration: none;
    font-family: inherit;
  }

  .btn:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }

  .btn:active {
    transform: scale(0.98);
  }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
  }

  .btn-primary:hover {
    background: var(--accent-hover);
    border-color: var(--accent-hover);
  }

  .btn-ghost {
    background: transparent;
    color: var(--text-secondary);
    border-color: var(--border);
  }

  .btn-ghost:hover {
    background: var(--bg);
    color: var(--text-primary);
    border-color: #cbd2da;
  }

  .btn-danger {
    background: transparent;
    color: var(--danger);
    border-color: transparent;
    padding: 0 8px;
    height: 28px;
    font-size: 12px;
    opacity: 0;
    transition: opacity 120ms, background 120ms, color 120ms;
  }

  .btn-danger:hover {
    background: var(--danger-subtle);
    color: var(--danger-hover);
  }

  .btn-danger:focus-visible {
    opacity: 1;
    outline: 2px solid var(--danger);
    outline-offset: 2px;
  }

  .btn-danger-solid {
    background: var(--danger);
    color: #fff;
    border-color: var(--danger);
  }

  .btn-danger-solid:hover {
    background: var(--danger-hover);
    border-color: var(--danger-hover);
  }

  /* Table card */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    overflow: hidden;
  }

  /* Table */
  table {
    width: 100%;
    border-collapse: collapse;
  }

  thead {
    border-bottom: 1px solid var(--border);
  }

  th {
    padding: 10px 16px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.03em;
    text-transform: uppercase;
    background: var(--bg);
  }

  th:last-child {
    text-align: right;
  }

  tbody tr {
    border-bottom: 1px solid var(--border-muted);
    transition: background 80ms;
  }

  tbody tr:last-child {
    border-bottom: none;
  }

  tbody tr:hover {
    background: #fafbfc;
  }

  tbody tr:hover .btn-danger {
    opacity: 1;
  }

  td {
    padding: 12px 16px;
    font-size: 13px;
    color: var(--text-primary);
    vertical-align: middle;
  }

  td:last-child {
    text-align: right;
  }

  .member-name {
    font-weight: 500;
  }

  .member-email {
    color: var(--text-secondary);
    font-size: 12px;
  }

  .role-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    background: var(--accent-subtle);
    color: var(--accent);
    border: 1px solid #bfdbfe;
  }

  .role-badge.admin {
    background: #faf5ff;
    color: #7c3aed;
    border-color: #ddd6fe;
  }

  .role-badge.viewer {
    background: var(--bg);
    color: var(--text-secondary);
    border-color: var(--border);
  }

  /* Skeleton loading */
  .skeleton-row td {
    padding: 12px 16px;
  }

  .skeleton {
    display: inline-block;
    height: 13px;
    border-radius: 4px;
    background: linear-gradient(90deg, #e9ecef 25%, #f3f5f7 50%, #e9ecef 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s ease-in-out infinite;
  }

  @keyframes shimmer {
    0% { background-position: 200% center; }
    100% { background-position: -200% center; }
  }

  /* Empty state */
  .empty-state {
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 64px 24px;
    text-align: center;
  }

  .empty-state.visible {
    display: flex;
  }

  .empty-icon {
    width: 64px;
    height: 64px;
    color: var(--text-muted);
    margin-bottom: 16px;
  }

  .empty-state h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 6px;
  }

  .empty-state p {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 20px;
    max-width: 260px;
    line-height: 1.6;
  }

  /* Modal overlay */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(17, 19, 24, 0.45);
    z-index: 100;
    align-items: center;
    justify-content: center;
  }

  .modal-overlay.open {
    display: flex;
  }

  .modal {
    background: var(--surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    width: 100%;
    max-width: 400px;
    margin: 16px;
    padding: 24px;
  }

  .modal-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .modal-body {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 24px;
  }

  .modal-body strong {
    color: var(--text-primary);
    font-weight: 500;
  }

  .modal-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }

  /* Toast */
  .toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 200;
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: var(--radius);
    border: 1px solid transparent;
    font-size: 13px;
    font-weight: 500;
    box-shadow: var(--shadow-md);
    pointer-events: auto;
    animation: toast-in 180ms ease-out;
    min-width: 220px;
    max-width: 340px;
  }

  @keyframes toast-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
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

  .toast-icon {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  /* Utility */
  .sr-only {
    position: absolute; width: 1px; height: 1px;
    padding: 0; margin: -1px; overflow: hidden;
    clip: rect(0,0,0,0); border: 0;
  }

  @media (prefers-reduced-motion: reduce) {
    .skeleton { animation: none; }
    .toast { animation: none; }
    .btn { transition: none; }
  }
</style>
</head>
<body>

<div class="layout">
  <div class="page-header">
    <div class="page-header-left">
      <h1>团队成员</h1>
      <p>管理成员权限与访问</p>
    </div>
    <button class="btn btn-primary" id="inviteBtn" onclick="handleInvite()">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
        <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      邀请成员
    </button>
  </div>

  <div class="card">
    <!-- Loading skeleton -->
    <div id="loadingView">
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody id="skeletonBody">
          <!-- JS renders skeletons -->
        </tbody>
      </table>
    </div>

    <!-- Member table -->
    <div id="tableView" style="display:none">
      <table>
        <thead>
          <tr>
            <th>姓名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody id="memberBody"></tbody>
      </table>
    </div>

    <!-- Empty state -->
    <div class="empty-state" id="emptyState">
      <svg class="empty-icon" viewBox="0 0 64 64" fill="none" aria-hidden="true">
        <circle cx="32" cy="22" r="10" stroke="currentColor" stroke-width="2"/>
        <path d="M12 54c0-11.046 8.954-20 20-20s20 8.954 20 20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M44 10v8M48 14h-8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
      </svg>
      <h3>还没有团队成员</h3>
      <p>邀请同事加入，共同协作管理项目</p>
      <button class="btn btn-primary" onclick="handleInvite()">邀请第一位成员</button>
    </div>
  </div>
</div>

<!-- Delete confirm modal -->
<div class="modal-overlay" id="deleteModal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal">
    <div class="modal-title" id="modalTitle">删除成员</div>
    <div class="modal-body" id="modalBody">确认后将移除该成员的所有访问权限。此操作<strong>无法撤销</strong>。</div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal()">取消</button>
      <button class="btn btn-danger-solid" onclick="confirmDelete()">删除成员</button>
    </div>
  </div>
</div>

<!-- Toast container -->
<div class="toast-container" id="toastContainer" aria-live="polite"></div>

<script>
  // --- Data ---
  const initialMembers = [
    { id: 1, name: '陈晓明', email: 'chenxm@company.com', role: 'admin' },
    { id: 2, name: '李雯雯', email: 'liww@company.com', role: 'editor' },
    { id: 3, name: '王浩然', email: 'wanghr@company.com', role: 'editor' },
    { id: 4, name: '张静怡', email: 'zhangjy@company.com', role: 'viewer' },
  ];

  const roleLabel = { admin: '管理员', editor: '编辑', viewer: '只读' };
  const roleClass = { admin: 'admin', editor: '', viewer: 'viewer' };

  let members = [];
  let pendingDeleteId = null;
  let nextId = 10;

  // --- Skeleton ---
  function renderSkeletons() {
    const body = document.getElementById('skeletonBody');
    const widths = [[100, 160, 52], [88, 148, 48], [110, 172, 52]];
    body.innerHTML = widths.map(([w1, w2, w3]) => `
      <tr class="skeleton-row">
        <td><span class="skeleton" style="width:${w1}px"></span></td>
        <td><span class="skeleton" style="width:${w2}px"></span></td>
        <td><span class="skeleton" style="width:${w3}px; height:20px; border-radius:4px"></span></td>
        <td style="text-align:right"><span class="skeleton" style="width:44px"></span></td>
      </tr>`).join('');
  }

  // --- Render table ---
  function renderTable() {
    const body = document.getElementById('memberBody');
    body.innerHTML = members.map(m => `
      <tr class="member-row" data-id="${m.id}">
        <td><span class="member-name">${esc(m.name)}</span></td>
        <td><span class="member-email">${esc(m.email)}</span></td>
        <td><span class="role-badge ${roleClass[m.role]}">${roleLabel[m.role]}</span></td>
        <td>
          <button class="btn btn-danger" onclick="openDeleteModal(${m.id})" aria-label="删除成员 ${esc(m.name)}">
            删除
          </button>
        </td>
      </tr>`).join('');
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  }

  // --- Show/hide views ---
  function showState() {
    document.getElementById('loadingView').style.display = 'none';
    if (members.length === 0) {
      document.getElementById('tableView').style.display = 'none';
      document.getElementById('emptyState').classList.add('visible');
    } else {
      document.getElementById('tableView').style.display = 'block';
      document.getElementById('emptyState').classList.remove('visible');
      renderTable();
    }
  }

  // --- Init: simulate loading ---
  renderSkeletons();
  setTimeout(() => {
    members = [...initialMembers];
    showState();
  }, 1400);

  // --- Delete flow ---
  function openDeleteModal(id) {
    pendingDeleteId = id;
    const member = members.find(m => m.id === id);
    if (!member) return;
    document.getElementById('modalBody').innerHTML =
      `确认后将移除 <strong>${esc(member.name)}</strong> 的所有访问权限。此操作<strong>无法撤销</strong>。`;
    document.getElementById('deleteModal').classList.add('open');
    // focus the cancel button by default (safer)
    setTimeout(() => document.querySelector('#deleteModal .btn-ghost').focus(), 30);
  }

  function closeModal() {
    document.getElementById('deleteModal').classList.remove('open');
    pendingDeleteId = null;
  }

  function confirmDelete() {
    const member = members.find(m => m.id === pendingDeleteId);
    const shouldFail = member && member.role === 'admin';
    closeModal();

    if (shouldFail) {
      showToast('error', '无法删除管理员：请先转让管理员权限');
      return;
    }

    if (member) {
      members = members.filter(m => m.id !== pendingDeleteId);
      showState();
      showToast('success', `${member.name} 已移出团队`);
    }
  }

  // ESC closes modal
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });

  // Click outside closes modal
  document.getElementById('deleteModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });

  // --- Invite ---
  function handleInvite() {
    // Simulate adding a new member for demo
    const demoMembers = [
      { name: '赵子轩', email: 'zhaozx@company.com', role: 'editor' },
      { name: '孙雅琪', email: 'sunyq@company.com', role: 'viewer' },
    ];
    const demo = demoMembers[nextId % demoMembers.length];
    members.push({ id: nextId++, ...demo });
    showState();
    showToast('success', `邀请已发送至 ${demo.email}`);
  }

  // --- Toast ---
  function showToast(type, message) {
    const container = document.getElementById('toastContainer');
    const icons = {
      success: `<svg class="toast-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M5 8l2 2 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
      error: `<svg class="toast-icon" viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M8 5v4M8 11v.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`,
    };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `${icons[type]}<span>${esc(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), type === 'success' ? 2200 : 4000);
  }
</script>
</body>
</html>
```

---

## 界面文案清单

### 按钮 label
| 位置 | 文案 |
|------|------|
| 顶部主操作按钮 | 邀请成员 |
| 空状态 CTA | 邀请第一位成员 |
| 行级删除按钮 | 删除 |
| 删除确认弹窗 - 取消 | 取消 |
| 删除确认弹窗 - 确认 | 删除成员 |

### 空状态文案
| 元素 | 文案 |
|------|------|
| 标题 | 还没有团队成员 |
| 说明文字 | 邀请同事加入，共同协作管理项目 |

### 加载文案
| 状态 | 呈现方式 | 说明 |
|------|---------|------|
| 成员列表加载中 | 行级 skeleton 动画（无文字） | 3 行占位骨架，尺寸与真实列等宽 |

### 删除确认弹窗文案
| 元素 | 文案 |
|------|------|
| 标题 | 删除成员 |
| 正文（含对象姓名） | 确认后将移除 **{姓名}** 的所有访问权限。此操作**无法撤销**。 |

### Toast 反馈文案
| 类型 | 文案 |
|------|------|
| 删除成功 | {姓名} 已移出团队 |
| 删除失败（管理员限制） | 无法删除管理员：请先转让管理员权限 |
| 邀请发送成功 | 邀请已发送至 {email} |
