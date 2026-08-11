# AgentSkill

这是一个用于集中保存、维护和分享可复用 AI Agent Skill 的仓库。

## 已收录 Skill

- [`feishu-chrome-reader`](./feishu-chrome-reader)：通过已登录的 Chrome 会话读取并提取飞书/Lark 文档内容。
- [`windows-sandbox-report-fallback`](./windows-sandbox-report-fallback)：当 Windows 沙箱限制阻止源码修改时，安全生成报告、指标等派生文件。
- [`audio-decode-guard`](./audio-decode-guard)：在本地录音转写前检查 FFmpeg，并在不修改源文件的前提下将压缩音频规范化为 Whisper 兼容的 WAV。
- [`upload-skill-to-github`](./upload-skill-to-github)：按安全审计、验证、精确暂存和提交推送流程，将用户级 Skill 上传到本仓库。

## 仓库约定

- 每个 Skill 使用独立目录，目录名与 `SKILL.md` 中的 `name` 保持一致。
- Skill 的主定义文件为 `SKILL.md`，可按需包含 `scripts/`、`references/`、`assets/` 和 `agents/`。
- 上传前必须检查敏感信息、危险命令、依赖安装、网络行为和实际文件清单。
- 不提交 `.env`、凭证、Token、私钥、用户原始媒体、测试数据、模型文件、第三方二进制、压缩缓存、`__pycache__` 或 `.pyc`。
- 提交前必须完成 Skill 结构验证、脚本语法检查和 `git diff --check`。
- 默认向 `main` 分支创建普通提交并推送，禁止强制推送和改写历史。

## 使用方式

进入目标 Skill 目录，阅读对应的 `SKILL.md`，根据其中的触发条件和工作流执行。需要安装到 WorkBuddy 用户级目录时，可将 Skill 目录复制到：

```text
~/.workbuddy/skills/<skill-name>/
```

安装或导入第三方 Skill 前，应先完成安全审计。
