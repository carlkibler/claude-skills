---
name: run
description: Generate a WiFi QR code PNG that phones can scan to join a network instantly. Use when the user wants to create a scannable WiFi QR code, generate WiFi credentials as a QR image, or embed a WiFi join code in a web page or document.
allowed-tools: Bash(uv run *)
---

# wifi-qr

Generate a WiFi QR code PNG phones can scan to join a network instantly.
Uses a self-contained `uv run` Python script — no pre-installed packages needed.

## Usage

```bash
uv run "${CLAUDE_SKILL_DIR}/generate-wifi-qr.py" \
  --ssid "My Network" \
  --password "s3cr3t" \
  --output /path/to/wifi-qr.png
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--ssid` | required | Network name |
| `--password` | `""` | Network password |
| `--security` | `WPA` | `WPA`, `WEP`, or `nopass` |
| `--output` | required | Destination PNG path |
| `--size` | `6` | Module size in pixels (larger = bigger image) |
| `--border` | `2` | Quiet-zone width in modules |

## Behavior

1. Builds the standard WiFi QR payload: `WIFI:T:WPA;S:<ssid>;P:<pass>;;`
   - Special chars in SSID/password are escaped per spec
2. Renders a PNG using `qrcode[pil]` (auto-installed by uv on first run)
3. Prints the output path, file size, and encoded payload for verification
4. Creates parent directories if needed

## Re-generation rule

Only re-run if SSID, password, or security type changes. The output file is
static — do **not** regenerate on every deploy or page render.

## Embedding in HTML

```html
<img src="/path/to/wifi-qr.png" alt="WiFi QR code"
     width="140" height="140"
     style="background:#fff; padding:8px; border-radius:6px; image-rendering:pixelated;">
```
