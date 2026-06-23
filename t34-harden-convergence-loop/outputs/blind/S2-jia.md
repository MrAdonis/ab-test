# report-gen 压力测试与修订方案

## 漏洞和风险逐项分析

**1. config.json 路径固死 `./config.json`，工作目录决定文件位置**

"固定路径"在实践中意味着必须从特定目录执行命令。三个人在不同机器上，常见行为是把工具装到 PATH 里全局运行，然后在任意目录调用——这时 `./config.json` 找的是当前目录而非工具所在目录，静默失败或报"文件不存在"。

处理：路径解析改为按优先级查找：① 当前工作目录 `./config.json`（兼容"在项目根运行"的习惯）→ ② 环境变量 `REPORT_GEN_CONFIG` 指定的路径 → ③ 工具找不到时打印清晰错误："config.json not found. Run from project root or set REPORT_GEN_CONFIG=/path/to/config.json"。不要默默输出空报告。

**2. "schema 固定不变"是假设，不是约束**

三人团队，迟早有人加字段、改键名、手写笔误。如果工具不做校验，坏数据要么静默跳过要么产生畸形 markdown，排查成本高。

处理：工具启动时对 config.json 做最小结构校验（顶层 `projects` 是数组，每个项目有 `name` 字符串）。校验失败立即 exit 1 并指出第几个条目哪个字段缺失，不继续生成报告。不需要 JSON Schema 库，手写 10 行校验就够。

**3. 输出只到 stdout，周报内容无法复用**

手动跑完看一眼没问题，但实际使用里三人大概率会 `> weekly.md` 重定向，然后文件名规范各自不同。一周后想翻上周的，各人文件散在不同位置。

处理：加一个可选 `--output <path>` 标志，指定时写入文件并打印"Report written to <path>"到 stderr（不污染 stdout 内容），不指定时照原来走 stdout。不强制，不改默认行为。

**4. 无版本信息，三人机器上可能跑不同版本**

"自己维护"意味着可能有人更新脚本、有人没更新，配合 config.json 的字段变化会出现无声兼容问题。

处理：在工具里硬编码一行 `VERSION = "1.0.0"`，`--version` 标志输出它。三人对齐时有个具体版本号可以对比，成本接近零。

**5. 错误处理缺位导致周报静默缺项**

项目列表里如果某个项目的某个字段是 null 或空字符串，模板字符串拼接要么输出空行要么抛异常。三个人看到不完整的报告可能以为项目真的没更新，不会往工具报错方向想。

处理：遍历项目生成时，缺少必填字段的条目跳过但在 stderr 打印警告："WARNING: project at index 2 missing 'name', skipped"。报告里所有跳过条目在末尾汇总一次，让人知道报告不完整。

**6. 没有可跑的自验方式**

三个人里有人改了工具逻辑，另外两个人下次跑可能拿到格式错的报告，不知道谁的版本对。

处理：附一个 `--dry-run` 标志，用内置的 fixture config（三行硬编码的假数据）生成报告输出到 stdout，不读任何外部文件。任何人改完工具跑一下 `report-gen --dry-run` 就能肉眼确认格式还对。这是最轻的自测方式，不需要测试框架。

---

## 修订后方案（可直接进入实现）

### 工具描述

内部 CLI `report-gen`，读配置文件生成 markdown 周报，输出到 stdout 或文件。

### 文件结构

```
report-gen/
├── report_gen.py      # 主入口，单文件实现
└── README.md          # 三行说明：安装方式 + 运行示例
```

单文件，无第三方依赖，Python 3 标准库即可。

### 配置文件解析

按优先级：
1. 环境变量 `REPORT_GEN_CONFIG` 指定的路径
2. 当前工作目录 `./config.json`

两处都找不到：exit 1，打印："config.json not found. Run from project root or set REPORT_GEN_CONFIG=/path/to/config.json"

### config.json 最小 schema

```json
{
  "projects": [
    {
      "name": "项目名",
      "status": "进行中",
      "updates": ["本周完成 X", "下周计划 Y"]
    }
  ]
}
```

`name` 和 `status` 必填。`updates` 可选，缺失时该项目区块不输出更新列表。

### 启动时校验

- `projects` 必须是数组且非空
- 每个条目有 `name`（非空字符串）和 `status`（非空字符串）
- 校验失败：exit 1，打印具体错误位置（"projects[1].name is missing or empty"）
- 校验通过后才开始生成

### 生成逻辑

- 每个项目输出一个二级标题 `## {name}`，下面一行状态，再下面是 updates 无序列表
- 缺失可选字段的条目跳过对应区块，不报错
- 有必填字段缺失的条目跳过整个条目，stderr 打印 WARNING
- 报告开头一行日期：`生成时间：YYYY-MM-DD`（取本机当天日期）
- 报告末尾，如有跳过条目汇总一行："注意：以下项目因配置不完整被跳过：X, Y"

### CLI 接口

```
report-gen [--output <path>] [--dry-run] [--version] [--help]
```

- 无参数：读 config，报告写 stdout
- `--output <path>`：报告写文件，写完后 stderr 打印 "Report written to <path>"
- `--dry-run`：忽略所有外部文件，用内置 fixture 生成报告写 stdout，用于验证工具本身
- `--version`：打印版本号 exit 0
- `--help`：打印用法 exit 0

### 安装方式

```bash
chmod +x report_gen.py
ln -s $(pwd)/report_gen.py /usr/local/bin/report-gen
```

三人各自在自己机器上执行一次。更新工具时重新 `git pull` 即可，symlink 不动。

### 验收条件

1. `report-gen --dry-run` 输出格式正确的 markdown，无报错
2. `report-gen` 在项目根（有 config.json）运行时输出完整报告
3. `report-gen` 在无 config.json 的目录运行时 exit 1 并打印有用的错误信息
4. config.json 有缺字段条目时，stderr 有 WARNING，stdout 报告不包含该条目
5. `--output weekly.md` 写出文件，内容与 stdout 模式相同
