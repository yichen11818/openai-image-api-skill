#!/usr/bin/env python3
"""Generate or edit images through an OpenAI Images API-compatible service."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import secrets
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_BASE_URL = "https://yjapi.manqiaotechnology.com"
DEFAULT_MODEL = "gpt-image-2.5-exact福利"
CONFIG_PATH = Path.home() / ".config" / "openai-image-api" / "config.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid config file {CONFIG_PATH}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"Invalid config file {CONFIG_PATH}: expected a JSON object")
    return data


def resolve_setting(cli_value: str | None, env_name: str, config: dict, key: str, default: str = "") -> str:
    return cli_value or os.environ.get(env_name, "") or str(config.get(key, "")) or default


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    return (args.prompt or "").strip()


def encode_multipart(fields: dict[str, str], images: list[Path]) -> tuple[bytes, str]:
    boundary = f"----image-api-{secrets.token_hex(16)}"
    chunks: list[bytes] = []

    def add(value: bytes) -> None:
        chunks.append(value)

    for name, value in fields.items():
        add(f"--{boundary}\r\n".encode())
        add(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        add(value.encode("utf-8"))
        add(b"\r\n")

    field_name = "image[]" if len(images) > 1 else "image"
    for image in images:
        mime = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
        add(f"--{boundary}\r\n".encode())
        add(f'Content-Disposition: form-data; name="{field_name}"; filename="{image.name}"\r\n'.encode("utf-8"))
        add(f"Content-Type: {mime}\r\n\r\n".encode())
        add(image.read_bytes())
        add(b"\r\n")

    add(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def request_json(url: str, api_key: str, body: bytes, content_type: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": content_type,
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(detail).get("error", {}).get("message", detail)
        except json.JSONDecodeError:
            message = detail
        raise SystemExit(f"Image API HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Image API request failed: {exc.reason}") from exc


def save_result(result: dict, output: Path, timeout: int) -> None:
    items = result.get("data") or []
    if not items or not isinstance(items[0], dict):
        error = result.get("error")
        message = error.get("message") if isinstance(error, dict) else None
        raise SystemExit(f"Image API returned no image data{': ' + message if message else ''}")

    item = items[0]
    output.parent.mkdir(parents=True, exist_ok=True)
    if item.get("b64_json"):
        output.write_bytes(base64.b64decode(item["b64_json"]))
    elif item.get("url"):
        try:
            download_request = urllib.request.Request(
                item["url"], headers={"User-Agent": "Mozilla/5.0 image-api-skill/1.0"}
            )
            with urllib.request.urlopen(download_request, timeout=timeout) as response:
                output.write_bytes(response.read())
        except urllib.error.URLError as exc:
            raise SystemExit(f"Image download failed: {exc.reason}") from exc
    else:
        raise SystemExit("Image API returned neither b64_json nor url")
    print(str(output.resolve()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument("--prompt", help="Image generation or edit prompt")
    prompt_group.add_argument("--prompt-file", help="UTF-8 text file containing the prompt")
    parser.add_argument("--image", action="append", default=[], help="Input image for edit mode; repeat for multiple")
    parser.add_argument("--output", required=True, help="Output image path")
    parser.add_argument("--size", default="1536x2048", help="Requested image size")
    parser.add_argument("--quality", help="Optional API quality value")
    parser.add_argument("--model", help="Image model override")
    parser.add_argument("--base-url", help="OpenAI-compatible API base URL")
    parser.add_argument("--api-key", help="API key override; prefer environment/config")
    parser.add_argument("--timeout", type=int, default=300, help="Request/download timeout in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    api_key = resolve_setting(args.api_key, "OPENAI_IMAGE_API_KEY", config, "api_key")
    base_url = resolve_setting(args.base_url, "OPENAI_IMAGE_BASE_URL", config, "base_url", DEFAULT_BASE_URL).rstrip("/")
    model = resolve_setting(args.model, "OPENAI_IMAGE_MODEL", config, "model", DEFAULT_MODEL)
    if not api_key:
        raise SystemExit("Missing API key. Set OPENAI_IMAGE_API_KEY or add api_key to " + str(CONFIG_PATH))

    prompt = read_prompt(args)
    if not prompt:
        raise SystemExit("Prompt is empty")

    images = [Path(value).expanduser().resolve() for value in args.image]
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        raise SystemExit("Input image not found: " + ", ".join(missing))

    if images:
        fields = {"model": model, "prompt": prompt, "n": "1", "size": args.size, "response_format": "url"}
        if args.quality:
            fields["quality"] = args.quality
        body, content_type = encode_multipart(fields, images)
        endpoint = "/v1/images/edits"
    else:
        payload: dict[str, str | int] = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": args.size,
            "response_format": "url",
        }
        if args.quality:
            payload["quality"] = args.quality
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        content_type = "application/json; charset=utf-8"
        endpoint = "/v1/images/generations"

    result = request_json(base_url + endpoint, api_key, body, content_type, args.timeout)
    save_result(result, Path(args.output).expanduser(), args.timeout)


if __name__ == "__main__":
    main()
