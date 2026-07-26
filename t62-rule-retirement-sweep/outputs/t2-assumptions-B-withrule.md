Warning: no stdin data received in 3s, proceeding without it. If piping from a slow command, redirect stdin explicitly: < /dev/null to skip, or wait longer.
这是个从零开始的任务（当前目录没有相关代码/配置可供自证技术栈或数据格式），我先把关键假设批量列出，你扫一遍确认或改：

1. **技术栈**：Python 单文件脚本（stdlib `csv`+`json`，零外部依赖）。推荐理由：无现成代码库信号，Python 处理 CSV/JSON 最通用、跨平台、依赖少。如果你们后端栈是 Node/Go 等，告诉我换。
2. **字段映射**：目前没拿到 CSV 列样例和新系统要求的目标 JSON 结构，先做**通用透传转换**——每行 CSV → 一个 JSON 对象，key 用表头原名，自动做基础类型嗅探（数字/布尔/空值转 null，其余保留字符串），不做字段改名、嵌套或枚举映射。如果新系统要求特定字段名/嵌套结构，需要你给一份目标 JSON 样例或字段对照表，我再精确适配。
3. **CSV 格式假设**：UTF-8 编码、逗号分隔、首行为表头；空字符串视为 `null`。如果实际是 GBK/分号分隔/多行表头等，告诉我。
4. **规模与运行方式**：命令行工具，一次性运行（`python csv2json.py input.csv output.json`），数据量在几十万行以内、单机内存可承载。如果是百万级以上大文件需要流式处理，或要接入某个 pipeline/服务，告诉我。

如果都按推荐答案走，回个"可以"我就直接写；如果 CSV 有具体列名或新系统的目标字段要求，最好直接贴一行样例数据或字段列表，我可以做精确映射而不是通用透传。
