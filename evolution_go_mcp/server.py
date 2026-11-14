"""MCP tools for Evolution API v2.3.7."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Evolution API")


def _request(method: str, path: str, data: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> Any:
    base_url = os.environ.get("EVOLUTION_GO_URL")
    api_key = os.environ.get("EVOLUTION_GO_KEY")
    if not base_url or not api_key:
        raise ValueError("Configure EVOLUTION_GO_URL and EVOLUTION_GO_KEY.")

    url = f"{base_url.rstrip('/')}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(
        url, data=body, method=method,
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


def _instance_path(path: str, instance: str) -> str:
    return f"{path}/{urllib.parse.quote(instance, safe='')}"


def _jid(number: str) -> str:
    return number if not number or "@" in number else f"{number}@s.whatsapp.net"


def _send_options(payload: dict[str, Any], delay: int | None, quoted: dict[str, Any] | None,
                  mentionAll: bool, mentionedJid: list[str] | None) -> dict[str, Any]:
    if delay is not None:
        payload["delay"] = delay
    if quoted:
        payload["quoted"] = quoted
    if mentionAll:
        payload["everyOne"] = True
    if mentionedJid:
        payload["mentioned"] = mentionedJid
    return payload


@mcp.tool()
def instances() -> Any:
    """List all instances using the global API key."""
    return _request("GET", "/instance/fetchInstances")


@mcp.tool()
def create_instance(name: str, token: str | None = None,
                    integration: Literal["WHATSAPP-BAILEYS", "WHATSAPP-BUSINESS", "EVOLUTION"] = "WHATSAPP-BAILEYS") -> Any:
    """Create an instance by name with a Baileys integration by default."""
    payload: dict[str, Any] = {"instanceName": name, "integration": integration}
    if token:
        payload["token"] = token
    return _request("POST", "/instance/create", payload)


@mcp.tool()
def connect(instance: str, number: str | None = None) -> Any:
    """Connect an instance and return its QR code or pairing code."""
    query = {"number": number} if number else None
    return _request("GET", _instance_path("/instance/connect", instance), query=query)


@mcp.tool()
def pair(instance: str, phone: str) -> Any:
    """Request a pairing code for an instance using its phone number."""
    return connect(instance, phone)


@mcp.tool()
def status(instance: str) -> Any:
    """Get the connection state of an instance."""
    return _request("GET", _instance_path("/instance/connectionState", instance))


@mcp.tool()
def qr(instance: str) -> Any:
    """Get the QR code for an instance that is awaiting connection."""
    return connect(instance)


@mcp.tool()
def logout(instance: str) -> Any:
    """Log out an instance and close its WhatsApp session."""
    return _request("DELETE", _instance_path("/instance/logout", instance))


@mcp.tool()
def delete_instance(instance: str) -> Any:
    """Delete an instance by its name."""
    return _request("DELETE", _instance_path("/instance/delete", instance))


@mcp.tool()
def summary() -> Any:
    """List the instances returned by Evolution API."""
    return instances()


@mcp.tool()
def send_text(instance: str, number: str, text: str, delay: int | None = None,
              quoted: dict[str, Any] | None = None, mentionAll: bool = False,
              mentionedJid: list[str] | None = None, linkPreview: bool = False) -> Any:
    """Send text to a plain phone number; quoted follows the Evolution API key/message shape."""
    payload: dict[str, Any] = {"number": number, "text": text}
    if linkPreview:
        payload["linkPreview"] = True
    payload = _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    return _request("POST", _instance_path("/message/sendText", instance), payload)


@mcp.tool()
def send_media(instance: str, number: str, url: str,
               type: Literal["image", "video", "audio", "document"],
               caption: str | None = None, filename: str | None = None,
               delay: int | None = None, quoted: dict[str, Any] | None = None,
               mentionAll: bool = False, mentionedJid: list[str] | None = None) -> Any:
    """Send media by URL or base64 data."""
    payload: dict[str, Any] = {"number": number, "media": url, "mediatype": type}
    if caption:
        payload["caption"] = caption
    if filename:
        payload["fileName"] = filename
    payload = _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    return _request("POST", _instance_path("/message/sendMedia", instance), payload)


@mcp.tool()
def send_location(instance: str, number: str, lat: float, lng: float,
                  name: str | None = None, address: str | None = None,
                  delay: int | None = None, quoted: dict[str, Any] | None = None,
                  mentionAll: bool = False, mentionedJid: list[str] | None = None) -> Any:
    """Send a location to a WhatsApp number."""
    payload: dict[str, Any] = {"number": number, "latitude": lat, "longitude": lng,
                              "name": name or "", "address": address or ""}
    payload = _send_options(payload, delay, quoted, mentionAll, mentionedJid)
    return _request("POST", _instance_path("/message/sendLocation", instance), payload)


@mcp.tool()
def send_contact(instance: str, number: str, fullName: str, phone: str,
                 org: str | None = None, delay: int | None = None,
                 quoted: dict[str, Any] | None = None, mentionAll: bool = False,
                 mentionedJid: list[str] | None = None) -> Any:
    """Send a contact card to a WhatsApp number."""
    contact: dict[str, Any] = {"fullName": fullName, "wuid": phone, "phoneNumber": phone}
    if org:
        contact["organization"] = org
    payload = _send_options({"number": number, "contact": [contact]}, delay, quoted, mentionAll, mentionedJid)
    return _request("POST", _instance_path("/message/sendContact", instance), payload)


@mcp.tool()
def send_link(instance: str, number: str, url: str, text: str,
              delay: int | None = None, quoted: dict[str, Any] | None = None) -> Any:
    """Send text with a preview generated from its URL."""
    content = f"{text.rstrip()}\n{url}" if text.strip() else url
    payload = _send_options({"number": number, "text": content, "linkPreview": True},
                             delay, quoted, False, None)
    return _request("POST", _instance_path("/message/sendText", instance), payload)


@mcp.tool()
def send_sticker(instance: str, number: str, sticker: str, delay: int | None = None,
                 quoted: dict[str, Any] | None = None, mentionAll: bool = False,
                 mentionedJid: list[str] | None = None) -> Any:
    """Send a sticker by URL or base64 data."""
    payload = _send_options({"number": number, "sticker": sticker}, delay, quoted, mentionAll, mentionedJid)
    return _request("POST", _instance_path("/message/sendSticker", instance), payload)


@mcp.tool()
def send_poll(instance: str, number: str, question: str, options: list[str],
              maxAnswer: int = 1, delay: int | None = None,
              quoted: dict[str, Any] | None = None) -> Any:
    """Send a poll with its question, options, and selectable answer count."""
    payload = _send_options({"number": number, "name": question, "values": options,
                             "selectableCount": maxAnswer}, delay, quoted, False, None)
    return _request("POST", _instance_path("/message/sendPoll", instance), payload)


@mcp.tool()
def react(instance: str, key: dict[str, Any], reaction: str) -> Any:
    """React to a message using its Evolution API message key."""
    return _request("POST", _instance_path("/message/sendReaction", instance),
                    {"key": key, "reaction": reaction})


@mcp.tool()
def edit_message(instance: str, number: str, key: dict[str, Any], message: str) -> Any:
    """Edit a sent message using its Evolution API message key."""
    return _request("POST", _instance_path("/chat/updateMessage", instance),
                    {"number": number, "key": key, "text": message})


@mcp.tool()
def delete_message(instance: str, remoteJid: str, id: str, fromMe: bool,
                   participant: str | None = None) -> Any:
    """Delete a message for everyone using its WhatsApp message key."""
    payload: dict[str, Any] = {"remoteJid": _jid(remoteJid), "id": id, "fromMe": fromMe}
    if participant:
        payload["participant"] = participant
    return _request("DELETE", _instance_path("/chat/deleteMessageForEveryone", instance), payload)


@mcp.tool()
def mark_read(instance: str, number: str, ids: list[str], fromMe: bool = False) -> Any:
    """Mark messages as read; incoming messages are read by default."""
    return _request("POST", _instance_path("/chat/markMessageAsRead", instance),
                    {"readMessages": [{"id": mid, "fromMe": fromMe, "remoteJid": _jid(number)}
                                      for mid in ids]})


@mcp.tool()
def message_status(instance: str, id: str) -> Any:
    """Get delivery updates for a message by ID."""
    return _request("POST", _instance_path("/chat/findStatusMessage", instance),
                    {"where": {"keyId": id}})


@mcp.tool()
def set_presence(instance: str, number: str, state: Literal["composing", "recording"],
                 delay: int = 1000) -> Any:
    """Set chat presence to composing or recording."""
    return _request("POST", _instance_path("/chat/sendPresence", instance),
                    {"number": number, "presence": state, "delay": delay})


def main() -> None:
    mcp.run(transport="stdio")

