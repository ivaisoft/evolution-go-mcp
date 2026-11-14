"""MCP tools for the Evolution Go REST API."""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Evolution Go")


def _request(method: str, path: str, data: dict[str, Any] | None = None) -> Any:
    base_url = os.environ.get("EVOLUTION_GO_URL")
    api_key = os.environ.get("EVOLUTION_GO_KEY")
    if not base_url or not api_key:
        raise ValueError("Configure EVOLUTION_GO_URL and EVOLUTION_GO_KEY.")

    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        data=body,
        method=method,
        headers={"apikey": api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else {"message": "success"}
    except urllib.error.HTTPError as error:
        try:
            details = json.loads(error.read())
        except (json.JSONDecodeError, UnicodeDecodeError):
            details = {"error": str(error)}
        raise RuntimeError(json.dumps({"error": f"HTTP {error.code}", "details": details})) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Connection failed: {error.reason}") from error


def _jid(number: str) -> str:
    return number if not number or "@" in number else f"{number}@s.whatsapp.net"


def _send_options(
    payload: dict[str, Any],
    delay: int | None,
    quoted: dict[str, Any] | None,
    mentionAll: bool,
    mentionedJid: list[str] | None,
) -> dict[str, Any]:
    if delay:
        payload["delay"] = delay
    if quoted:
        payload["quoted"] = quoted
    if mentionAll:
        payload["mentionAll"] = True
    if mentionedJid:
        payload["mentionedJid"] = mentionedJid
    return payload


@mcp.tool()
def instances() -> Any:
    """List all Evolution Go instances."""
    return _request("GET", "/instance/all")


@mcp.tool()
def create_instance(name: str, token: str | None = None) -> Any:
    """Create an instance, optionally with an auth token."""
    payload: dict[str, Any] = {"instanceName": name}
    if token:
        payload["token"] = token
    return _request("POST", "/instance/create", payload)


@mcp.tool()
def connect(phone: str, webhook: str, immediate: bool = False, subscribe: list[str] | None = None) -> Any:
    """Connect the instance with a phone number and webhook."""
    payload: dict[str, Any] = {"phone": phone, "webhook": webhook}
    if immediate:
        payload["immediate"] = True
    if subscribe:
        payload["subscribe"] = subscribe
    return _request("POST", "/instance/connect", payload)


@mcp.tool()
def disconnect() -> Any:
    """Disconnect the current instance."""
    return _request("POST", "/instance/disconnect")


@mcp.tool()
def status() -> Any:
    """Get the current instance status."""
    return _request("GET", "/instance/status")


@mcp.tool()
def qr() -> Any:
    """Get the QR code for pairing."""
    return _request("GET", "/instance/qr")


@mcp.tool()
def pair(phone: str) -> Any:
    """Request a pairing code for a phone number."""
    return _request("POST", "/instance/pair", {"phone": phone})


@mcp.tool()
def logout() -> Any:
    """Log out the current instance."""
    return _request("DELETE", "/instance/logout")


@mcp.tool()
def delete_instance(instanceId: str) -> Any:
    """Delete an instance by its ID."""
    return _request("DELETE", f"/instance/delete/{instanceId}")


@mcp.tool()
def delete_proxy(instanceId: str) -> Any:
    """Remove the proxy from an instance."""
    return _request("DELETE", f"/instance/proxy/{instanceId}")


@mcp.tool()
def summary() -> Any:
    """List all instances with their returned instance details."""
    instances_data = _request("GET", "/instance/all")
    if isinstance(instances_data, list):
        entries = [
            {
                "instance": instance.get("instanceName") or instance.get("name") or instance.get("id", "unknown"),
                "raw": instance,
            }
            for instance in instances_data
        ]
        return {"instances": entries, "total": len(entries)}
    return instances_data


@mcp.tool()
def send_text(
    number: str,
    text: str,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a text message with optional delay, quote, and mentions."""
    payload = _send_options(
        {"number": _jid(number), "text": text}, delay, quoted, mentionAll, mentionedJid
    )
    return _request("POST", "/send/text", payload)


@mcp.tool()
def send_media(
    number: str,
    url: str,
    type: Literal["image", "video", "audio", "document"],
    caption: str | None = None,
    filename: str | None = None,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send media by URL, with optional caption, filename, and send options."""
    payload: dict[str, Any] = {"number": _jid(number), "mediaUrl": url, "mediatype": type}
    if caption:
        payload["caption"] = caption
    if filename:
        payload["fileName"] = filename
    return _request(
        "POST", "/send/media", _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    )


@mcp.tool()
def send_location(
    number: str,
    lat: float,
    lng: float,
    name: str | None = None,
    address: str | None = None,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a location with optional name, address, and send options."""
    payload: dict[str, Any] = {"number": _jid(number), "latitude": lat, "longitude": lng}
    if name:
        payload["name"] = name
    if address:
        payload["address"] = address
    return _request(
        "POST", "/send/location", _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    )


@mcp.tool()
def send_contact(
    number: str,
    fullName: str,
    phone: str,
    org: str | None = None,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a contact card with optional organization and send options."""
    contact: dict[str, Any] = {"fullName": fullName, "phoneNumber": phone}
    if org:
        contact["organization"] = org
    payload = _send_options(
        {"number": _jid(number), "contact": contact}, delay, quoted, mentionAll, mentionedJid
    )
    return _request("POST", "/send/contact", payload)


@mcp.tool()
def send_link(
    number: str,
    url: str,
    text: str,
    title: str | None = None,
    description: str | None = None,
    imgUrl: str | None = None,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a link preview with optional metadata and send options."""
    payload: dict[str, Any] = {"number": _jid(number), "url": url, "text": text}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if imgUrl:
        payload["thumbnailUrl"] = imgUrl
    return _request(
        "POST", "/send/link", _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    )


@mcp.tool()
def send_sticker(
    number: str,
    sticker: str,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a sticker by URL with optional send options."""
    payload = _send_options(
        {"number": _jid(number), "stickerUrl": sticker}, delay, quoted, mentionAll, mentionedJid
    )
    return _request("POST", "/send/sticker", payload)


@mcp.tool()
def send_poll(
    number: str,
    question: str,
    options: list[str],
    maxAnswer: int | None = None,
    delay: int | None = None,
    quoted: dict[str, Any] | None = None,
    mentionAll: bool = False,
    mentionedJid: list[str] | None = None,
) -> Any:
    """Send a poll with options and optional send settings."""
    payload: dict[str, Any] = {
        "number": _jid(number),
        "question": question,
        "options": options,
    }
    if maxAnswer:
        payload["maxAnswer"] = maxAnswer
    return _request(
        "POST", "/send/poll", _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    )


@mcp.tool()
def react(number: str, id: str, reaction: str) -> Any:
    """React to a message with an emoji."""
    return _request(
        "POST", "/message/react", {"number": _jid(number), "messageId": id, "reaction": reaction}
    )


@mcp.tool()
def edit_message(chat: str, id: str, message: str) -> Any:
    """Edit a sent message."""
    return _request("POST", "/message/edit", {"chat": chat, "messageId": id, "message": message})


@mcp.tool()
def delete_message(chat: str, id: str) -> Any:
    """Delete a message for everyone."""
    return _request("POST", "/message/delete", {"chat": chat, "messageId": id})


@mcp.tool()
def mark_read(number: str, ids: list[str]) -> Any:
    """Mark messages as read."""
    return _request("POST", "/message/markread", {"number": _jid(number), "messageIds": ids})


@mcp.tool()
def message_status(id: str) -> Any:
    """Get message delivery status."""
    return _request("POST", "/message/status", {"messageId": id})


@mcp.tool()
def set_presence(number: str, state: Literal["composing", "recording"], isAudio: bool = False) -> Any:
    """Set chat presence to composing or recording."""
    payload: dict[str, Any] = {"number": _jid(number), "state": state}
    if isAudio:
        payload["isAudio"] = True
    return _request("POST", "/message/presence", payload)


def main() -> None:
    mcp.run(transport="stdio")
