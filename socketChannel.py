import logging
import warnings
import uuid
from typing import Optional, Text, Any, List, Dict, Callable, Awaitable, Iterable

from sanic import Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from socketio import AsyncServer

from rasa.core.channels.channel import InputChannel
from rasa.core.channels.channel import UserMessage, OutputChannel

logger = logging.getLogger(__name__)

class SocketBlueprint(Blueprint):
    def __init__(self, sio: AsyncServer, socketio_path: Text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = sio  # Use self.ctx for AsyncServer instance
        self.ctx.socketio_path = socketio_path

    def register(self, app, options=None):
        if options is None:
            options = {}
        self.ctx.attach(app, self.ctx.socketio_path)
        super().register(app, options)

class SocketIOOutput(OutputChannel):
    @classmethod
    def name(cls) -> Text:
        return "socketio"

    def __init__(self, sio: AsyncServer, sid: Text, bot_message_evt: Text) -> None:
        self.sio = sio
        self.sid = sid
        self.bot_message_evt = bot_message_evt

    async def _send_message(self, socket_id: Text, message: Dict[Text, Any]) -> None:
        """Sends a message to the recipient using the bot event."""
        await self.sio.emit(self.bot_message_evt, message, room=socket_id)

    async def send_text_message(
        self, recipient_id: Text, text: Text, **kwargs: Any
    ) -> None:
        """Send a message through this channel."""
        await self._send_message(self.sid, {"text": text})

    async def send_image_url(
        self, recipient_id: Text, image: Text, **kwargs: Any
    ) -> None:
        """Sends an image to the output"""
        message = {"attachment": {"type": "image", "payload": {"src": image}}}
        await self._send_message(self.sid, message)

    async def send_text_with_buttons(
        self,
        recipient_id: Text,
        text: Text,
        buttons: List[Dict[Text, Any]],
        **kwargs: Any,
    ) -> None:
        """Sends buttons to the output."""
        message = {"text": text, "quick_replies": []}
        for button in buttons:
            message["quick_replies"].append(
                {
                    "content_type": "text",
                    "title": button.get("title"),
                    "payload": button.get("payload"),
                }
            )
        await self._send_message(self.sid, message)

    async def send_elements(
        self, recipient_id: Text, elements: Iterable[Dict[Text, Any]], **kwargs: Any
    ) -> None:
        """Sends elements to the output."""
        for element in elements:
            message = {
                "attachment": {
                    "type": "template",
                    "payload": {"template_type": "generic", "elements": [element]},
                }
            }
            await self._send_message(self.sid, message)

    async def send_custom_json(
        self, recipient_id: Text, json_message: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends custom json to the output"""
        json_message.setdefault("room", self.sid)
        await self.sio.emit(self.bot_message_evt, **json_message)

    async def send_attachment(
        self, recipient_id: Text, attachment: Dict[Text, Any], **kwargs: Any
    ) -> None:
        """Sends an attachment to the user."""
        await self._send_message(self.sid, {"attachment": attachment})


class SocketIOInput(InputChannel):
    """A socket.io input channel."""

    @classmethod
    def name(cls) -> Text:
        return "socketio"

    @classmethod
    def from_credentials(cls, credentials: Optional[Dict[Text, Any]]) -> InputChannel:
        credentials = credentials or {}
        return cls(
            credentials.get("user_message_evt", "user_uttered"),
            credentials.get("bot_message_evt", "bot_uttered"),
            credentials.get("namespace"),
            credentials.get("session_persistence", False),
            credentials.get("socketio_path", "/socket.io"),
        )

    def __init__(
        self,
        user_message_evt: Text = "user_uttered",
        bot_message_evt: Text = "bot_uttered",
        namespace: Optional[Text] = None,
        session_persistence: bool = False,
        socketio_path: Text = "/socket.io",
    ) -> None:
        self.bot_message_evt = bot_message_evt
        self.session_persistence = session_persistence
        self.user_message_evt = user_message_evt
        self.namespace = namespace
        self.socketio_path = socketio_path

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[Any]]
    ) -> Blueprint:
        sio = AsyncServer(async_mode="sanic", cors_allowed_origins=[])  # Initialize AsyncServer
        socketio_webhook = SocketBlueprint(
            sio, self.socketio_path, "socketio_webhook", __name__
        )

        @socketio_webhook.route("/", methods=["GET"])
        async def health(_: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @sio.event
        async def connect(sid: Text, _):
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.event
        async def disconnect(sid: Text):
            logger.debug(f"User {sid} disconnected from socketIO endpoint.")

        @sio.event
        async def session_request(sid: Text, data: Optional[Dict[Text, Any]]):
            if data is None:
                data = {}
            if "session_id" not in data or data["session_id"] is None:
                data["session_id"] = uuid.uuid4().hex
            await sio.emit("session_confirm", data["session_id"], room=sid)
            logger.debug(f"User {sid} connected to socketIO endpoint.")

        @sio.event
        async def handle_message(sid: Text, data: Dict[Text, Any]):
            output_channel = SocketIOOutput(sio, sid, self.bot_message_evt)

            if self.session_persistence:
                if not data.get("session_id"):
                    warnings.warn(
                        "A message without a valid sender_id "
                        "was received. This message will be "
                        "ignored. Make sure to set a proper "
                        "session id using the "
                        "`session_request` socketIO event."
                    )
                    return

                sender_id = data["session_id"]
            else:
                sender_id = sid

            message = UserMessage(
                data["message"], output_channel, sender_id, input_channel=self.name(), metadata=data.get("customData")
            )
            await on_new_message(message)

        return socketio_webhook
