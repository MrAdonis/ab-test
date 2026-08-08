MCP 让 Claude Code 能连外部数据源和工具,Skills 是打包好的领域知识和工作流程给模型读。两者不是替代关系,是分层:MCP 解决"连得上",Skills 解决"做得对"。

日常写代码,MCP 该配的配好就不用管了(cloudflare-docs、chrome-devtools 这类),真正决定输出质量的是 Skills——design-system、coding-dod 这些规则文件才是每次调用时真正影响行为的东西。

很多人纠结"该做 MCP server 还是 Skill",其实问错了问题:需要新增能力接口(读数据库、调 API)才是 MCP,需要把已有能力用对(遵循规范、走对流程)是 Skill。前者扩展 agent 能干什么,后者约束 agent 怎么干。
