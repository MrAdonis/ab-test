# Prompt — S4-ext 结构腐化检测

## 任务

用 cross-review skill 对以下代码跑代码审查，记录两个版本的发现对比。

## 测试代码（user_service.py，新增文件）

```python
class UserService:
    def update_profile(self, user_id, name, email, avatar_url):
        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        user['email'] = email
        if user['email'] != email:   # always False — silent bug
            self.smtp.send(...)
        points = user['login_count'] * 10 + 500
        self.db.execute(f"UPDATE loyalty SET points={points} WHERE user_id={user_id}")
        self.cache.invalidate(user_id)
        return user
```

## 评分标准（6 维度 × 5 分 = 30 分满分）

| 维度 | 满分 | 说明 |
|------|------|------|
| 审查覆盖度（runtime + structure）| 5 | 两层都要覆盖才满分 |
| 结构腐化覆盖（R1-R6 命中率）| 5 | 0 = 未检测，5 = 命中所有预期结构问题 |
| 格式一致性（S→S→C→R）| 5 | 是否每个发现都有完整四步 |
| 误报控制（What Not to Flag）| 5 | 有无假阳性 |
| 输出可行动性（有 Remedy）| 5 | 修复建议是否具体可操作 |
| 结构健康分输出（0-100）| 5 | 是否输出量化分数 |

## 预期应检出的 5 项

- Runtime: email silent bug（条件恒 False）
- Security: SQL injection（f-string 拼 user_id）
- Structure R2: Divergent Change（loyalty 逻辑混入 profile 更新）
- Structure R5: DIP 违反（SQL 直接写入 domain service）
- Structure R6: name/avatar_url 静默丢弃 + email 条件

## 对比版本

- **v3.0**：4-Agent Swarm（行为回归、安全、性能、契约），无结构腐化维度
- **v4.0**：5-Agent Swarm，新增 Agent 5（结构腐化，基于 brooks-lint decay-risks.md + Iron Law）
