`rm` 删的是工作区文件，Git 不追踪未提交的改动，所以没法从 Git 恢复。这是我的失误——给删除命令之前应该先确认目标路径下有没有未提交的变更，没做这一步。

现在能做的：如果文件系统没有覆写过，可以试 `strings /dev/null` 不行，但可以用 `photorec` 或 macOS 的 `diskutil` 碰碰运气——不过成功率不高，尤其 SSD 上。如果你开了 Time Machine，`tmutil compare` 或直接进 `/Volumes/com.apple.TimeMachine…` 找快照是最稳的路。

下次遇到删除操作，我会先跑 `git status` 确认干净再继续。
