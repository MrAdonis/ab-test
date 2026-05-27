你是 AB test 中的 baseline 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

任务：用户给了一段 React 组件代码 + 4 条反馈，请按反馈修改代码并返回修改后的完整代码。最后简要说明你做了什么改动。

代码：
```jsx
function UserCard({ user }) {
  const handleClick = () => {
    console.log('clicked')
    window.location.href = '/users/' + user.id
  }
  return (
    <div onClick={handleClick} style={{cursor: 'pointer'}}>
      <img src={user.avatar} alt="" />
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  )
}
```

用户反馈（4 条，混合优先级，未标级）：
1. img 缺少 alt 文本（无障碍问题）
2. 整张卡片用 onClick 而不是 <a> 标签，键盘用户无法访问
3. 变量名可以从 handleClick 改成更具体的，比如 navigateToUser
4. window.location.href 拼接 user.id 时 URL 没有 encode

输出格式：
1. 修改后的完整代码
2. 简短说明改了什么

不要写其他东西，不要建议进一步改动，不要输出文件。在 ≤300 字内完成。