---
name: upload-skill-to-github
description: This skill should be used whenever the user asks to save, publish, push, sync, back up, or upload a WorkBuddy/Codex Skill to GitHub. Unless the user explicitly gives another repository, always use https://github.com/Ziggymi/AgentSkill.git, place each Skill in its own top-level directory, update the Chinese repository README, audit the Skill, validate it, commit only intended source files, and push to main without rewriting history.
agent_created: true
---

# 上传 Skill 到 GitHub

## 目标

把已完成的用户级或项目级 Skill 安全同步到固定仓库 `https://github.com/Ziggymi/AgentSkill.git`。默认把以后创建的所有 Skill 都保存到这个仓库；只有用户在当前任务中明确指定其他仓库时才改变目标。

## 固定约定

- 默认仓库：`https://github.com/Ziggymi/AgentSkill.git`
- 默认分支：`main`
- 目录结构：仓库根目录下的 `<skill-name>/`
- Skill 名称：目录名必须与 `SKILL.md` frontmatter 中的 `name` 一致。
- 仓库根 `README.md`：使用简体中文，并在“已收录 Skill”中维护链接和一句话说明。
- 提交方式：创建普通提交并推送；禁止 `push --force`、改写历史或删除其他 Skill。

## 工作流

### 1. 确定源 Skill

优先从以下位置查找：

1. 用户明确给出的目录；
2. `~/.workbuddy/skills/<skill-name>/`；
3. 当前项目 `.workbuddy/skills/<skill-name>/`。

完整读取 `SKILL.md`，确认名称、描述和资源引用。读取全部脚本及相关文档，不把未审查文件直接上传。

### 2. 执行安全审计

在安装、创建或上传 Skill 前，加载 `skills-security-check` 并进行静态审计。至少检查：

- 危险命令、远程下载并执行、权限提升和隐蔽执行；
- 凭证、Token、API Key、密码、私钥和 `.env`；
- 敏感目录读取与数据外送；
- 全局依赖安装、未固定版本和不可信下载源；
- Skill 描述与脚本实际行为是否一致。

存在 P0/Malicious 时停止上传并明确警告。存在 P1/Suspicious 时先修复；无法修复时取得用户明确确认。P2/Benign 才进入后续步骤。

### 3. 确定允许上传的文件

默认只允许：

- `SKILL.md`
- `scripts/` 中必要的源代码
- `references/` 中必要的说明文档
- `assets/` 中确实属于 Skill 的小型资源
- `agents/` 中必要的 Agent 元数据
- Skill 自身的 `README.md`（如果存在）

默认排除：

- `.env`、凭证、Token、私钥、Cookie、登录数据
- 用户原始音频、视频、图片、文档和测试数据
- FFmpeg、模型、第三方可执行文件、DLL 和安装包
- ZIP 包、构建产物、日志和临时文件
- `__pycache__/`、`.pyc`、`node_modules/`、虚拟环境、缓存目录
- 与 Skill 无关的工作区文件

除非用户明确要求且已审计，禁止上传二进制和个人材料。

### 4. 准备本地仓库

优先复用当前工作区已存在且远程地址完全匹配的 `AgentSkill` 克隆。不存在时克隆到当前工作区的 `AgentSkill/`。

执行前检查：

- `git status --short --branch`
- `git remote -v`
- 当前分支和 `origin/main` 的关系
- 是否存在他人的未提交修改

发现非本任务改动时不得覆盖、暂存或回滚；应隔离自己的改动，必要时暂停并询问用户。

### 5. 同步 Skill 源码

将审计通过的文件复制到仓库 `<skill-name>/`。更新现有 Skill 时先读取仓库版本，只修改目标 Skill 的必要文件。

不得使用宽泛复制把整个工作区带入仓库。不得执行会删除未知文件的镜像同步、清空目录或递归删除。

### 6. 更新中文 README

保持根 `README.md` 为简体中文。若 Skill 尚未列出，在“已收录 Skill”中添加：

```markdown
- [`<skill-name>`](./<skill-name>)：<一句中文说明>。
```

同步维护仓库安全约定，避免重复条目，不改变其他 Skill 的正确说明。

### 7. 验证提交内容

按顺序执行：

1. 从已安装的内置 `skill-creator/scripts/quick_validate.py` 定位验证器，使用 WorkBuddy 受管 Python 分别验证源 Skill 和仓库副本；不要假定目标 Skill 自带验证器；
2. 对 Python 脚本执行 `py_compile` 或等价语法检查；
3. 搜索凭证和敏感信息；
4. 执行 `git diff --check`；
5. 执行 `git status --short --untracked-files=all`；
6. 阅读目标文件的最终差异。

只用精确路径执行 `git add`，禁止 `git add .` 或 `git add -A`。再次查看 `git diff --cached --stat` 和 `git status --short`，确认暂存区只有目标文件。

### 8. 提交并推送

使用清晰的英文提交标题，例如：

```text
Add <skill-name> skill
Update <skill-name> skill
```

推送到 `origin main`。禁止强制推送、rebase 改写已发布历史或跳过 hooks。推送失败时保留提交，报告错误并修复根因，不重复创建相同提交。

### 9. 线上验证与汇报

打开并验证：

```text
https://github.com/Ziggymi/AgentSkill/tree/main/<skill-name>
```

最终汇报仓库、分支、Skill 目录、提交短哈希、访问链接和明确排除的敏感/大型文件。若本次产生可查看链接，用结果展示入口打开线上目录。

## 禁止事项

- 不把 GitHub 凭证写入 Skill、仓库或日志。
- 不读取或输出用户的 SSH 私钥、浏览器 Cookie 或个人访问令牌。
- 不上传原始录音、转写材料或与 Skill 无关的个人文件。
- 不执行 `git add .`、`git add -A`、`git push --force`、`git reset --hard`。
- 不因上传 Skill 而删除本地用户级 Skill。
