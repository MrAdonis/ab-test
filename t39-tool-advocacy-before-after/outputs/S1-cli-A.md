想让 AI 帮你操作 Blender、FreeCAD 这类没有 API 的软件？港大 HKUDS 开源的 CLI-Anything，能把任意 GUI 软件或已有 API 封装成命令行工具，Claude Code、OpenClaw 这些 agent 拿到手就能直接调用。

它自动分析目标软件的操作界面，生成对应的 CLI 命令、测试用例和使用文档，不用你手写适配代码。跑起来之后 AI 操作的是真实软件，返回结构化 JSON，agent 能直接读懂结果继续干活，不是靠截图瞎猜。

官方 demo：AI 用 Blender 和 FreeCAD 协作设计出一辆火星车模型；另一个 demo 是全自动剪出带字幕的视频。这些原本都得人工在界面上一步步点。

GitHub 搜 HKUDS/CLI-Anything，README 里有安装步骤和示例仓库，喂给它一个新软件的名字，它自己摸索接口。

给 AI agent 攒工具箱的，这条收藏起来。
