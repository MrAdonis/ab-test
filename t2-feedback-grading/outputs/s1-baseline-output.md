```jsx
function UserCard({ user }) {
  return (
    <a href={`/users/${encodeURIComponent(user.id)}`} style={{ display: 'block', textDecoration: 'none', cursor: 'pointer' }}>
      <img src={user.avatar} alt={`${user.name} 的头像`} />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </a>
  )
}
```

**改动说明：**

1. 整张卡片改为 `<a>` 标签，键盘可访问，移除 `onClick` + `handleClick`（同时顺带解决了变量命名问题，函数已无必要保留）
2. `img` 的 `alt` 补上有意义的文本
3. URL 用模板字符串 + `encodeURIComponent` 处理 `user.id`