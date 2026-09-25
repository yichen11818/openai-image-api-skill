# OpenAI Image API Skill

用于 Codex 的图片生成与编辑 skill，通过兼容 OpenAI Images API 的服务完成文生图、单图编辑及多图参考。

## 功能

- 文生图：调用 /v1/images/generations。
- 图生图：调用 /v1/images/edits，支持重复传入 --image，保留参考图顺序。
- 支持自定义 API Key、Base URL、模型、尺寸和质量。
- 支持 URL 或 Base64 图片响应，输出保存为本地文件。
- 仅使用 Python 标准库，无需第三方依赖；建议 Python 3.10 或更高版本。

## 安装到 Codex

克隆到 Codex skills 目录，目录名称使用 openai-image-api。若已安装同名 skill，请先检查现有目录。

    git clone https://github.com/yichen11818/openai-image-api-skill.git "$HOME/.codex/skills/openai-image-api"

在 Codex 中输入：用 $openai-image-api 生成一张……；提供参考图时使用编辑模式。

## 快速开始：把 API 地址和 Key 配好即可生图

安装 skill 后，向 Codex 提供图片服务的 API 地址和 API Key，让它完成本地配置，然后直接描述想生成的图片。API Key 也可以先写入本地配置，再让 Codex 使用，避免在对话中粘贴。服务需要兼容 OpenAI Images API；如果服务不支持默认模型，还需提供该服务支持的模型名称。

可以把下面这段话发给 Codex，替换其中的占位值：

```text
请配置全局 $openai-image-api skill：
API 地址：https://你的图片服务地址
API Key：<你的 API Key；或说明已保存到本地配置>
模型：<服务支持的模型名；支持默认模型时可以省略>

请将配置保存在 ~/.config/openai-image-api/config.json，保留已有的其他配置。
不要在回复、日志或 Git 提交中输出真实 Key。
配置完成后，用这个 skill 生成一张水彩风格的山间日出图片，保存到本地并展示结果。
```

配置一次后，后续直接提需求即可，例如：

- 文生图：“帮我生成一张咖啡店开业海报，暖色调，文案是「周末见」。”
- 图生图：附上参考图，再说“保持商品外观，把背景换成白色摄影棚。”
- 多图合成：按顺序上传图片，再说“用第一张作背景，把第二张的商品放进去。”

生成后由 Codex 检查实际图片；文字海报还需核对中文、数字等内容，并在有明显错误时修正。

## 让 Codex 加入全局提示词

如果希望以后只要提出生图或改图需求，Codex 就优先使用这个 skill，可以把下面整段发给 Codex。这里只提供设置指令；克隆仓库本身不会自动修改全局提示词。

```text
请将以下规则加入我的 Codex 全局提示词文件（通常是 ~/.codex/AGENTS.md；如果设置了 CODEX_HOME，则使用该目录下的 AGENTS.md）。
先读取现有文件，保留其他规则；已有同名章节时更新该章节，避免重复添加。

## 全局图片生成与编辑

- 用户提出生图、图片生成、海报、封面、插画、商品图、Logo、背景图，或改图、图生图、重绘、风格迁移、抠图、换背景、局部修改、多图合成等需求时，第一优先调用全局 `$openai-image-api` skill。
- 用户提供一张或多张参考图片时，使用该 skill 的 `edit` / 图生图模式，并按用户给出的顺序传入图片；只有纯文本创作图片时才使用 `generate` 模式。
- 生成完成后必须检查实际图片；文字型海报重点核对中文、数字、日期、品牌名和免责声明，发现明显错误时应迭代修正后再交付。
- 用户明确指定其他图片模型、服务或 skill 时，遵循用户选择，不强制改用 `$openai-image-api`。
- 不得在回复、日志或生成物中输出 API Key 或图片签名 URL，只交付保存后的本地图片文件。
```

## 配置

配置优先级：命令行参数 > 环境变量 > 用户本地配置文件。

| 设置 | 参数 | 环境变量 | 配置字段 |
| --- | --- | --- | --- |
| API Key | --api-key | OPENAI_IMAGE_API_KEY | api_key |
| API 地址 | --base-url | OPENAI_IMAGE_BASE_URL | base_url |
| 模型 | --model | OPENAI_IMAGE_MODEL | model |

本地配置路径：~/.config/openai-image-api/config.json，Windows 下位于用户主目录。示例仅含占位值：

    {
      "api_key": "YOUR_API_KEY",
      "base_url": "https://your-image-api.example",
      "model": "YOUR_IMAGE_MODEL"
    }

Base URL 填服务根地址，不要附加 /v1，脚本会自动拼接完整接口路径。使用服务商实际支持的模型、尺寸、quality 与 response_format；不同兼容服务的支持情况可能不同。

保留原脚本默认值：Base URL 为 https://yjapi.manqiaotechnology.com，模型为 gpt-image-2.5-exact福利，尺寸为 1536x2048。使用其他服务时请显式覆盖地址和模型。默认值不表示服务可用性保证。

真实密钥仅保存在本地配置或环境变量中，不要提交到 GitHub。

## 命令行用法

以下命令在仓库根目录运行，API Key、地址和模型从本地配置或环境变量读取。

文生图：

    py -3 scripts/image_api.py --prompt "A watercolor landscape" --output output/landscape.png

图生图：

    py -3 scripts/image_api.py --prompt-file prompt.txt --image source.png --output output/edited.png

多图参考：

    py -3 scripts/image_api.py --prompt-file prompt.txt --image background.png --image logo.png --output output/poster.png

prompt.txt 使用 UTF-8 编码。macOS / Linux 可将 py -3 替换为 python3。

查看全部参数：

    py -3 scripts/image_api.py --help

## 文件结构

- SKILL.md：skill 执行说明。
- agents/openai.yaml：Codex 界面名称与触发配置。
- scripts/image_api.py：图片 API 客户端。

发布时检查 Python 语法及命令行帮助；没有执行收费的图片 API 调用。
