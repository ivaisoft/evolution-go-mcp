import importlib
import sys
import types
import unittest
from unittest.mock import patch

mcp = types.ModuleType("mcp")
server_module = types.ModuleType("mcp.server")
fastmcp_module = types.ModuleType("mcp.server.fastmcp")


class FastMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        return lambda function: function

    def run(self, transport):
        pass


fastmcp_module.FastMCP = FastMCP
sys.modules.setdefault("mcp", mcp)
sys.modules.setdefault("mcp.server", server_module)
sys.modules.setdefault("mcp.server.fastmcp", fastmcp_module)
sys.path.insert(0, ".")

server = importlib.import_module("evolution_go_mcp.server")


class RouteTests(unittest.TestCase):
    def request(self, function, *args, expected, **kwargs):
        with patch.object(server, "_request", return_value="ok") as request:
            self.assertEqual(function(*args, **kwargs), "ok")
        actual = request.call_args.args + tuple(request.call_args.kwargs.values())
        self.assertEqual(actual, expected)

    def test_instance_routes(self):
        self.request(server.instances, expected=("GET", "/instance/fetchInstances"))
        self.request(server.create_instance, "test",
                     expected=("POST", "/instance/create",
                               {"instanceName": "test", "integration": "WHATSAPP-BAILEYS"}))
        self.request(server.connect, "my instance",
                     expected=("GET", "/instance/connect/my%20instance", None))
        self.request(server.connect, "test", "+15551234567",
                     expected=("GET", "/instance/connect/test", {"number": "+15551234567"}))
        self.request(server.pair, "test", "+15551234567",
                     expected=("GET", "/instance/connect/test", {"number": "+15551234567"}))
        self.request(server.qr, "test", expected=("GET", "/instance/connect/test", None))
        self.request(server.status, "test",
                     expected=("GET", "/instance/connectionState/test"))
        self.request(server.logout, "test", expected=("DELETE", "/instance/logout/test"))
        self.request(server.delete_instance, "test", expected=("DELETE", "/instance/delete/test"))

    def test_send_routes_and_api_v2_payloads(self):
        self.request(server.send_text, "inst", "5511999999999", "hello", linkPreview=True,
                     expected=("POST", "/message/sendText/inst",
                               {"number": "5511999999999", "text": "hello", "linkPreview": True}))
        self.request(server.send_media, "inst", "5511999999999", "https://example.test/a.png", "image",
                     expected=("POST", "/message/sendMedia/inst",
                               {"number": "5511999999999", "media": "https://example.test/a.png", "mediatype": "image"}))
        self.request(server.send_location, "inst", "5511999999999", -23.5, -46.6,
                     expected=("POST", "/message/sendLocation/inst",
                               {"number": "5511999999999", "latitude": -23.5, "longitude": -46.6, "name": "", "address": ""}))
        self.request(server.send_contact, "inst", "5511999999999", "Teste", "5521999999999",
                     expected=("POST", "/message/sendContact/inst",
                               {"number": "5511999999999", "contact": [
                                   {"fullName": "Teste", "wuid": "5521999999999",
                                    "phoneNumber": "5521999999999"}]}))
        self.request(server.send_link, "inst", "5511999999999", "https://example.test", "Link",
                     expected=("POST", "/message/sendText/inst",
                               {"number": "5511999999999", "text": "Link\nhttps://example.test",
                                "linkPreview": True}))
        self.request(server.send_sticker, "inst", "5511999999999", "https://example.test/a.webp",
                     expected=("POST", "/message/sendSticker/inst",
                               {"number": "5511999999999", "sticker": "https://example.test/a.webp"}))
        self.request(server.send_poll, "inst", "5511999999999", "Color?", ["red", "blue"], 1,
                     expected=("POST", "/message/sendPoll/inst",
                               {"number": "5511999999999", "name": "Color?", "values": ["red", "blue"],
                                "selectableCount": 1}))
        key = {"id": "m1", "fromMe": False, "remoteJid": "5511999999999@s.whatsapp.net"}
        self.request(server.react, "inst", key, "👍",
                     expected=("POST", "/message/sendReaction/inst", {"key": key, "reaction": "👍"}))

    def test_chat_routes_and_payloads(self):
        key = {"id": "m1", "fromMe": True, "remoteJid": "5511999999999@s.whatsapp.net"}
        self.request(server.edit_message, "inst", "5511999999999", key, "edited",
                     expected=("POST", "/chat/updateMessage/inst",
                               {"number": "5511999999999", "key": key, "text": "edited"}))
        self.request(server.delete_message, "inst", "5511999999999", "m1", True,
                     expected=("DELETE", "/chat/deleteMessageForEveryone/inst",
                               {"remoteJid": "5511999999999@s.whatsapp.net", "id": "m1", "fromMe": True}))
        self.request(server.mark_read, "inst", "5511999999999", ["m1"],
                     expected=("POST", "/chat/markMessageAsRead/inst",
                               {"readMessages": [{"id": "m1", "fromMe": False,
                                                  "remoteJid": "5511999999999@s.whatsapp.net"}]}))
        self.request(server.message_status, "inst", "m1",
                     expected=("POST", "/chat/findStatusMessage/inst", {"where": {"keyId": "m1"}}))
        self.request(server.set_presence, "inst", "5511999999999", "composing",
                     expected=("POST", "/chat/sendPresence/inst",
                               {"number": "5511999999999", "presence": "composing", "delay": 1000}))

    def test_send_options_use_api_v2_field_names(self):
        self.request(server.send_text, "inst", "123", "hello", delay=5, mentionAll=True,
                     mentionedJid=["123@s.whatsapp.net"],
                     expected=("POST", "/message/sendText/inst",
                               {"number": "123", "text": "hello", "delay": 5,
                                "everyOne": True, "mentioned": ["123@s.whatsapp.net"]}))


if __name__ == "__main__":
    unittest.main()

