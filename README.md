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
