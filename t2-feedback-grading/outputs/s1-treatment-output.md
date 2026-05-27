severity 识别：

- 第 1 条：**Must** — `alt=""` 空字符串让屏幕阅读器跳过图片，头像图应有有意义的描述，属无障碍硬缺陷
- 第 2 条：**Must** — `div onClick` 键盘用户无法 Tab 聚焦、无法 Enter 触发，属可访问性阻塞问题
- 第 3 条：**Nit** — 纯命名偏好，不影响功能
- 第 4 条：**Must** — `user.id` 若含特殊字符会构造出畸形 URL，属功能正确性 bug

---

```jsx
function UserCard({ user }) {
  return (
    <a href={`/users/${encodeURIComponent(user.id)}`}>
      <img src={user.avatar} alt={`${user.name} 的头像`} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </a>
  )
}
```

---

**改了什么：**

- 第 1 条（Must）：`alt` 填入 `user.name` 相关描述
- 第 2 条（Must）：整个卡片换成 `<a>` 标签，删去 `onClick` 和内联 `cursor` 样式（`<a>` 默认可键盘访问，`cursor: pointer` 由 CSS 统一处理即可）；同时顺手删掉了 `console.log`
- 第 4 条（Must）：改用模板字符串 + `encodeURIComponent`

**没改：** 第 3 条（Nit）— `handleClick` 已随 `<a>` 重构被整体移除，命名问题自然消失，无需单独处理。