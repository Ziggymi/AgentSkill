# 沙箱绕行

当 Codex 桌面版在 Windows 上执行 `apply_patch` 时遇到多可写根目录或受限令牌沙箱错误，本 Skill 用于安全完成报告、指标、JSON、Markdown 等生成型产物。

典型错误：

```text
windows unelevated restricted-token sandbox cannot enforce split writable root sets
```

## 能做什么

- 先确认故障发生在补丁沙箱初始化阶段，而不是项目文件、Git 或代码本身
- 优先运行项目已有脚本，生成基础报告或数据产物
- 在不修改项目源码的前提下，通过项目运行时生成补充指标和计时结果
- 处理 JavaScript、PowerShell、Python 多层调用中的路径、编码和换行转义
- 对生成的 JSON、Markdown、数量、标签和乱码进行最终校验

## 安全边界

- 不关闭沙箱，不修改 ACL，不扩大可写目录
- 不把 `Set-Content`、重定向或 Python 文件重写当作源码编辑后门
- 仅用于生成报告、预测结果、指标、导出数据等派生产物
- 如果任务必须修改源码，则在用户规定的重试次数后停止并报告待应用补丁

## 已验证的 Windows 规则

- PowerShell 向 Python 传递源码时使用单引号 here-string
- Windows 可执行文件路径使用正斜杠，例如 `D:/Apps/Python/python.exe`
- JavaScript 模板字符串中避免原始 Markdown 反引号
- 多层解析时使用 `chr(10).join(lines)` 生成换行
- 向原生程序传递中文前显式设置 PowerShell UTF-8 输出编码
- 网络调用只在子进程内清除已确认无效的代理，并申请范围明确的网络授权

## 安装

将 `windows-sandbox-report-fallback` 目录复制到个人 Codex Skills 目录：

```text
%USERPROFILE%\.codex\skills\windows-sandbox-report-fallback
```

重启或刷新 Codex 后即可发现该 Skill，界面显示名称为“沙箱绕行”。

## 文件

- `SKILL.md`：Codex 使用的流程与安全规则
- `agents/openai.yaml`：界面显示名称和默认提示词
- `README.md`：面向使用者的说明
