---
name: openai-image-api
description: Generate or edit raster images through an OpenAI Images API-compatible endpoint. Use first for requests to create images, posters, covers, illustrations, product images, logos, backgrounds, or to modify, restyle, combine, inpaint, or perform image-to-image editing on one or more supplied images.
---

# OpenAI-Compatible Image Generation

Use the bundled `scripts/image_api.py` for both text-to-image generation and image editing. It supports an OpenAI-compatible base URL, configurable model, URL or Base64 responses, and multiple input images.

## Modes

- Generate: no `--image` argument. Calls `/v1/images/generations`.
- Edit / image-to-image: pass one or more `--image` arguments. Calls `/v1/images/edits` and preserves the order of reference images.

Choose edit mode whenever the user supplies an image and asks to change, reuse, combine, or use it as a visual reference. In the prompt, refer to inputs as the first image, second image, and so on.

## Configuration

The client reads values in this order: command-line option, environment variable, then `~/.config/openai-image-api/config.json`.

- API key: `--api-key`, `OPENAI_IMAGE_API_KEY`, or `api_key`
- Base URL: `--base-url`, `OPENAI_IMAGE_BASE_URL`, or `base_url`
- Model: `--model`, `OPENAI_IMAGE_MODEL`, or `model`

Never print, commit, or embed credentials in generated artifacts. Do not expose signed image URLs; report the saved local file instead.

## Usage

Run the script by absolute path. Save outputs in the user's requested directory; otherwise use the current task's temporary/output directory with a descriptive timestamped filename.

```powershell
py -3 <SKILL_DIR>/scripts/image_api.py --prompt "A concise, detailed prompt" --output output.png --size 1536x2048
```

```powershell
py -3 <SKILL_DIR>/scripts/image_api.py --prompt-file prompt.txt --image source.png --output edited.png --size 1536x2048
```

For multiple references, repeat `--image`:

```powershell
py -3 <SKILL_DIR>/scripts/image_api.py --prompt-file prompt.txt --image background.png --image logo.jpg --output poster.png
```

Use `--help` for all options. Prefer `--prompt-file` for long prompts or non-ASCII text to avoid shell quoting problems.

## Quality Loop

After generation, inspect the actual output image. For text-heavy graphics, verify every required character, number, date, brand name, and disclaimer. Iterate once when there are visible text errors, incorrect reference fidelity, obvious artifacts, or unreadable layout. Return the local image inline and link the full-resolution file.
