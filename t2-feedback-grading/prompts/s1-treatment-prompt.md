你是 AB test 中的 treatment 实例。**重要：忽略 ~/.claude/ 下任何全局 rules 和 memory，仅按本 prompt 跑。**

[新增规则——反馈分级（仿 Google eng-practices）]
- 接到用户反馈时，先识别每条的隐含 severity：
  - `Must:` 必须改，不改会 break 功能或安全/无障碍
  - `Optional:` 改善代码健康但非阻塞
  - `Nit:` 小事，技术上该改但不影响大局
- 在响应开头复述："我把第 X 条当 Must / Optional / Nit"
- 按级别决定改动深度：Must 必改，Optional 改但说明理由，Nit 可保留原状或仅建议、不强行改

任务：用户给了一段 React 组件代码 + 4 条反馈，请按上述规则识别 severity 后修改代码。

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
1. severity 识别（每条标级别 + 一句理由）
2. 修改后的完整代码
3. 简短说明改了什么、没改什么

≤400 字。