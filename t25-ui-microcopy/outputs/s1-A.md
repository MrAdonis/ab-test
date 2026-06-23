# Variant A - 团队成员管理后台实现

```html
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>团队成员管理</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif;
    font-size: 13px;
    line-height: 1.4;
    background: #f5f5f5;
    color: #1a1a1a;
    min-height: 100vh;
  }

  /* Layout */
  .app {
    max-width: 960px;
    margin: 0 auto;
    padding: 32px 24px;
  }

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  .page-title {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
  }

  .page-subtitle {
    font-size: 12px;
    color: #6b6b6b;
    margin-top: 2px;
  }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0 14px;
    height: 32px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-family: inherit;
    cursor: pointer;
    transition: background 120ms ease-out, opacity 120ms ease-out;
    outline: none;
    white-space: nowrap;
  }

  .btn:focus-visible {
    outline: 2px solid #0066cc;
    outline-offset: 2px;
  }

  .btn-primary {
    background: #1a1a1a;
    color: #fff;
    font-weight: 500;
  }

  .btn-primary:hover { background: #333; }
  .btn-primary:active { transform: scale(0.98); }

  .btn-ghost {
    background: transparent;
    color: #1a1a1a;
    border: 1px solid #d4d4d4;
  }

  .btn-ghost:hover { background: #f0f0f0; }
  .btn-ghost:active { transform: scale(0.98); }

  .btn-danger {
    background: transparent;
    color: #c0392b;
    border: 1px solid #e8c8c5;
    font-size: 12px;
    height: 28px;
    padding: 0 10px;
  }

  .btn-danger:hover { background: #fdf3f2; }
  .btn-danger:active { transform: scale(0.98); }

  .btn-sm {
    height: 28px;
    padding: 0 10px;
    font-size: 12px;
  }

  /* Table card */
  .table-card {
    background: #fff;
    border: 1px solid #e4e4e4;
    border-radius: 8px;
    overflow: hidden;
  }

  /* Table */
  table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
  }

  thead {
    border-bottom: 1px solid #e4e4e4;
  }

  th {
    padding: 10px 16px;
    text-align: left;
    font-size: 11px;
    font-weight: 600;
    color: #6b6b6b;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    background: #fafafa;
    white-space: nowrap;
  }

  th:nth-child(1) { width: 22%; }
  th:nth-child(2) { width: 32%; }
  th:nth-child(3) { width: 22%; }
  th:nth-child(4) { width: 24%; }

  td {
    padding: 12px 16px;
    vertical-align: middle;
    border-bottom: 1px solid #f0f0f0;
  }

  tr:last-child td { border-bottom: none; }

  tbody tr { transition: background 80ms ease-out; }
  tbody tr:hover { background: #fafafa; }

  .member-name {
    font-weight: 500;
    color: #1a1a1a;
  }

  .member-email {
    color: #4b4b4b;
    font-size: 12px;
    font-variant-numeric: tabular-nums;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  /* Role badge */
  .role-badge {
    display: inline-flex;
    align-items: center;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 500;
    line-height: 18px;
  }

  .role-admin {
    background: #eef2ff;
    color: #3730a3;
  }

  .role-member {
    background: #f0fdf4;
    color: #166534;
  }

  .role-viewer {
    background: #f9fafb;
    color: #6b6b6b;
    border: 1px solid #e4e4e4;
  }

  /* Actions column */
  .td-actions {
    text-align: right;
  }

  /* Skeleton rows */
  .skeleton-row td { padding: 14px 16px; }

  .skeleton {
    display: inline-block;
    height: 12px;
    border-radius: 4px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.4s infinite;
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .skeleton-name { width: 96px; }
  .skeleton-email { width: 156px; }
  .skeleton-role { width: 52px; }
  .skeleton-action { width: 48px; float: right; }

  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 64px 24px;
  }

  .empty-icon {
    width: 40px;
    height: 40px;
    margin: 0 auto 16px;
    color: #c4c4c4;
  }

  .empty-title {
    font-size: 14px;
    font-weight: 500;
    color: #4b4b4b;
    margin-bottom: 6px;
  }

  .empty-desc {
    font-size: 12px;
    color: #9b9b9b;
    margin-bottom: 20px;
    line-height: 1.6;
  }

  /* Modal overlay */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    opacity: 0;
    pointer-events: none;
    transition: opacity 180ms ease-out;
  }

  .modal-overlay.visible {
    opacity: 1;
    pointer-events: auto;
  }

  .modal {
    background: #fff;
    border-radius: 12px;
    width: 100%;
    max-width: 400px;
    margin: 16px;
    padding: 24px;
    transform: translateY(8px);
    transition: transform 180ms ease-out;
    box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  }

  .modal-overlay.visible .modal { transform: translateY(0); }

  .modal-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 8px;
  }

  .modal-desc {
    font-size: 13px;
    color: #4b4b4b;
    line-height: 1.6;
    margin-bottom: 24px;
  }

  .modal-desc strong { color: #1a1a1a; }

  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }

  .btn-modal-danger {
    background: #c0392b;
    color: #fff;
    font-weight: 500;
  }

  .btn-modal-danger:hover { background: #a93226; }
  .btn-modal-danger:active { transform: scale(0.98); }

  /* Toast */
  .toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    z-index: 200;
  }

  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: #1a1a1a;
    color: #fff;
    border-radius: 8px;
    font-size: 13px;
    min-width: 240px;
    max-width: 360px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transform: translateX(16px);
    opacity: 0;
    transition: transform 200ms ease-out, opacity 200ms ease-out;
  }

  .toast.visible {
    transform: translateX(0);
    opacity: 1;
  }

  .toast-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .toast-success .toast-dot { background: #4ade80; }
  .toast-error { background: #1a1a1a; }
  .toast-error .toast-dot { background: #f87171; }

  /* Count label */
  .member-count {
    font-size: 12px;
    color: #9b9b9b;
    font-variant-numeric: tabular-nums;
  }

  @media (prefers-reduced-motion: reduce) {
    .skeleton { animation: none; background: #f0f0f0; }
    .modal, .modal-overlay, .toast, .btn { transition: none; }
  }
</style>
</head>
<body>

<div class="app">
  <div class="page-header">
    <div>
      <div class="page-title">团队成员</div>
      <div class="page-subtitle member-count" id="memberCount">加载中…</div>
    </div>
    <button class="btn btn-primary" onclick="openInviteModal()" aria-label="邀请新成员加入团队">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
        <path d="M7 1v12M1 7h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      邀请成员
    </button>
  </div>

  <div class="table-card">
    <table>
      <thead>
        <tr>
          <th>姓名</th>
          <th>邮箱</th>
          <th>角色</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        <!-- skeleton rows -->
        <tr class="skeleton-row">
          <td><span class="skeleton skeleton-name"></span></td>
          <td><span class="skeleton skeleton-email"></span></td>
          <td><span class="skeleton skeleton-role"></span></td>
          <td><span class="skeleton skeleton-action"></span></td>
        </tr>
        <tr class="skeleton-row">
          <td><span class="skeleton" style="width:80px"></span></td>
          <td><span class="skeleton" style="width:180px"></span></td>
          <td><span class="skeleton skeleton-role"></span></td>
          <td><span class="skeleton skeleton-action"></span></td>
        </tr>
        <tr class="skeleton-row">
          <td><span class="skeleton" style="width:112px"></span></td>
          <td><span class="skeleton" style="width:140px"></span></td>
          <td><span class="skeleton skeleton-role"></span></td>
          <td><span class="skeleton skeleton-action"></span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- 删除确认弹窗 -->
<div class="modal-overlay" id="deleteModal" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal">
    <div class="modal-title" id="modalTitle">移除成员</div>
    <div class="modal-desc" id="modalDesc">
      确定要移除 <strong id="targetName"></strong> 吗？<br>
      该成员将立即失去对团队资源的访问权限，此操作不可撤销。
    </div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal()">取消</button>
      <button class="btn btn-primary btn-modal-danger" onclick="confirmDelete()">确认移除</button>
    </div>
  </div>
</div>

<!-- Toast 容器 -->
<div class="toast-container" id="toastContainer" aria-live="polite"></div>

<script>
  // 模拟数据
  let members = [
    { id: 1, name: '陈思远', email: 'siyuan.chen@acme.io', role: 'admin' },
    { id: 2, name: '林晓燕', email: 'xiaoyan.lin@acme.io', role: 'member' },
    { id: 3, name: '刘雅婷', email: 'yating.liu@acme.io', role: 'member' },
    { id: 4, name: '王磊', email: 'lei.wang@acme.io', role: 'viewer' },
  ];

  let pendingDeleteId = null;

  const ROLE_LABELS = { admin: '管理员', member: '成员', viewer: '只读' };
  const ROLE_CLASS = { admin: 'role-admin', member: 'role-member', viewer: 'role-viewer' };

  function renderTable() {
    const tbody = document.getElementById('tableBody');
    const count = document.getElementById('memberCount');

    if (members.length === 0) {
      count.textContent = '暂无成员';
      tbody.innerHTML = `
        <tr>
          <td colspan="4">
            <div class="empty-state">
              <svg class="empty-icon" viewBox="0 0 40 40" fill="none" aria-hidden="true">
                <circle cx="20" cy="14" r="7" stroke="currentColor" stroke-width="1.5"/>
                <path d="M6 36c0-7.732 6.268-14 14-14s14 6.268 14 14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
              <div class="empty-title">还没有团队成员</div>
              <div class="empty-desc">邀请同事加入团队后，<br>他们将出现在这里。</div>
              <button class="btn btn-primary" onclick="openInviteModal()">邀请第一位成员</button>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    count.textContent = `共 ${members.length} 位成员`;
    tbody.innerHTML = members.map(m => `
      <tr>
        <td><span class="member-name">${m.name}</span></td>
        <td><span class="member-email" title="${m.email}">${m.email}</span></td>
        <td><span class="role-badge ${ROLE_CLASS[m.role]}">${ROLE_LABELS[m.role]}</span></td>
        <td class="td-actions">
          <button class="btn btn-danger" onclick="openDeleteModal(${m.id}, '${m.name}')" aria-label="移除成员 ${m.name}">移除</button>
        </td>
      </tr>
    `).join('');
  }

  function openDeleteModal(id, name) {
    pendingDeleteId = id;
    document.getElementById('targetName').textContent = name;
    document.getElementById('deleteModal').classList.add('visible');
    document.querySelector('#deleteModal .btn-ghost').focus();
  }

  function closeModal() {
    document.getElementById('deleteModal').classList.remove('visible');
    pendingDeleteId = null;
  }

  function confirmDelete() {
    if (pendingDeleteId === null) return;

    // 模拟 30% 概率失败
    const shouldFail = Math.random() < 0.3;
    closeModal();

    setTimeout(() => {
      if (shouldFail) {
        showToast('移除失败：服务器返回 500，请稍后重试', 'error');
      } else {
        members = members.filter(m => m.id !== pendingDeleteId);
        renderTable();
        showToast('成员已移除', 'success');
      }
      pendingDeleteId = null;
    }, 400);
  }

  function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span class="toast-dot"></span><span>${message}</span>`;
    container.appendChild(toast);

    requestAnimationFrame(() => {
      requestAnimationFrame(() => toast.classList.add('visible'));
    });

    const duration = type === 'success' ? 2000 : 4000;
    setTimeout(() => {
      toast.classList.remove('visible');
      setTimeout(() => toast.remove(), 220);
    }, duration);
  }

  function openInviteModal() {
    showToast('邀请功能即将上线', 'success');
  }

  // 模拟加载：1.2s 后渲染列表
  setTimeout(() => {
    renderTable();
  }, 1200);

  // 点击遮罩关闭弹窗
  document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
  });

  // ESC 关闭弹窗
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });
</script>
</body>
</html>
```

---

## 界面文案清单

### 顶部操作
- **主按钮**：`邀请成员`
- **页面副标题（加载中）**：`加载中…`
- **页面副标题（有数据）**：`共 N 位成员`
- **页面副标题（无数据）**：`暂无成员`

### 表头
- `姓名` / `邮箱` / `角色` / `操作`

### 角色标签
- `管理员` / `成员` / `只读`

### 行级操作
- **删除按钮**：`移除`
- **删除按钮 aria-label**：`移除成员 [姓名]`

### 加载状态（Skeleton）
- 无文案，纯骨架屏动画

### 空状态
- **标题**：`还没有团队成员`
- **说明**：`邀请同事加入团队后，他们将出现在这里。`
- **空状态 CTA 按钮**：`邀请第一位成员`

### 删除确认弹窗
- **弹窗标题**：`移除成员`
- **说明正文**：`确定要移除 [姓名] 吗？该成员将立即失去对团队资源的访问权限，此操作不可撤销。`
- **取消按钮**：`取消`
- **确认按钮**：`确认移除`

### Toast 反馈
- **删除成功**：`成员已移除`（绿点，1.5s）
- **删除失败**：`移除失败：服务器返回 500，请稍后重试`（红点，4s）
- **邀请功能占位**：`邀请功能即将上线`（绿点，2s）
