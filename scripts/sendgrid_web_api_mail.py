#!/usr/bin/env python3
"""Send email through the SendGrid Web API.

Usage example:
  export SENDGRID_API_KEY="SG.xxxxx"
  export SENDGRID_FROM_EMAIL="weather-bot@example.com"
  python3 scripts/sendgrid_web_api_mail.py \
    --to "pneborg@berkadia.com" \
    --subject "Weather report" \
    --text "Forecast goes here"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

SENDGRID_ENDPOINT = "https://api.sendgrid.com/v3/mail/send"
REQUEST_TIMEOUT_SECONDS = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a message with SendGrid Web API.")
    parser.add_argument("--to", required=True, help="Recipient email address.")
    parser.add_argument("--subject", required=True, help="Email subject line.")
    parser.add_argument(
        "--text",
        help="Plain text message body. Use this or --stdin-text or --html.",
    )
    parser.add_argument(
        "--stdin-text",
        action="store_true",
        help="Read plain text message body from stdin.",
    )
    parser.add_argument(
        "--html",
        help="HTML message body (optional).",
    )
    parser.add_argument(
        "--from-email",
        default=os.getenv("SENDGRID_FROM_EMAIL"),
        help="Sender email. Defaults to SENDGRID_FROM_EMAIL.",
    )
    parser.add_argument(
        "--from-name",
        default=os.getenv("SENDGRID_FROM_NAME"),
        help="Sender display name. Defaults to SENDGRID_FROM_NAME.",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("SENDGRID_API_KEY"),
        help="SendGrid API key. Defaults to SENDGRID_API_KEY.",
    )
    return parser.parse_args()


def get_message_text(args: argparse.Namespace) -> str:
    if args.stdin_text:
        return sys.stdin.read()
    return args.text or ""


def validate_args(args: argparse.Namespace, text_content: str) -> None:
    if not args.api_key:
        raise ValueError("Missing SendGrid API key. Set SENDGRID_API_KEY or pass --api-key.")
    if not args.from_email:
        raise ValueError("Missing sender email. Set SENDGRID_FROM_EMAIL or pass --from-email.")
    if not text_content and not args.html:
        raise ValueError("Provide content with --text, --stdin-text, or --html.")


def build_payload(args: argparse.Namespace, text_content: str) -> dict:
    content = []
    if text_content:
        content.append({"type": "text/plain", "value": text_content})
    if args.html:
        content.append({"type": "text/html", "value": args.html})

    from_object = {"email": args.from_email}
    if args.from_name:
        from_object["name"] = args.from_name

    return {
        "personalizations": [{"to": [{"email": args.to}]}],
        "from": from_object,
        "subject": args.subject,
        "content": content,
    }


def send_email(api_key: str, payload: dict) -> None:
    request_body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        SENDGRID_ENDPOINT,
        data=request_body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        status_code = response.getcode()
        response_body = response.read().decode("utf-8")
        print(f"SendGrid response status: {status_code}")
        if response_body:
            print(response_body)


def main() -> int:
    try:
        args = parse_args()
        text_content = get_message_text(args)
        validate_args(args, text_content)
        payload = build_payload(args, text_content)
        send_email(args.api_key, payload)
        return 0
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        print(f"SendGrid HTTP error: {error.code}", file=sys.stderr)
        if details:
            print(details, file=sys.stderr)
        return 1
    except Exception as error:  # noqa: BLE001
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
