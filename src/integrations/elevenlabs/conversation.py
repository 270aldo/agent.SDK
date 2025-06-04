import os
import logging
from io import BytesIO
from typing import Optional
from dotenv import load_dotenv

try:
    from elevenlabs import ElevenLabs
    from elevenlabs.conversational_ai import Conversation
    from elevenlabs.conversational_ai.conversation import AudioInterface
except Exception as e:  # pragma: no cover - library may not be installed in tests
    ElevenLabs = None  # type: ignore
    Conversation = None  # type: ignore
    AudioInterface = object  # type: ignore
    logging.getLogger(__name__).warning(f"ElevenLabs import failed: {e}")

load_dotenv()
logger = logging.getLogger(__name__)


class BufferedAudioInterface(AudioInterface):
    """Simple audio interface that stores audio output in memory."""

    def __init__(self) -> None:
        self.buffer = BytesIO()

    def start(self, input_callback):  # type: ignore[override]
        # This engine only handles text input, so we ignore the callback
        pass

    def stop(self) -> None:  # type: ignore[override]
        pass

    def output(self, audio: bytes) -> None:  # type: ignore[override]
        self.buffer.write(audio)

    def interrupt(self) -> None:  # type: ignore[override]
        pass


class ConversationalEngine:
    """Wrapper around ElevenLabs conversational AI."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.client = ElevenLabs(api_key=self.api_key) if ElevenLabs else None
        self.conversation: Optional[Conversation] = None
        self.audio_interface = BufferedAudioInterface()

    def start(self, agent_id: str, requires_auth: bool = True) -> None:
        if not self.client or not Conversation:
            raise RuntimeError("ElevenLabs client not available")
        self.conversation = Conversation(
            client=self.client,
            agent_id=agent_id,
            requires_auth=requires_auth,
            audio_interface=self.audio_interface,
        )
        self.conversation.start_session()

    def send_message(self, text: str) -> None:
        if not self.conversation:
            raise RuntimeError("Conversation not started")
        self.conversation.send_user_message(text)

    def end(self) -> Optional[str]:
        if not self.conversation:
            return None
        self.conversation.end_session()
        conv_id = self.conversation.wait_for_session_end()
        self.conversation = None
        return conv_id

    def get_audio(self) -> BytesIO:
        return BytesIO(self.audio_interface.buffer.getvalue())
