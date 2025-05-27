"""
Unit tests for the ConversationService.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.services.conversation_service import ConversationService
from src.services.personalization_service import PersonalizationService
from src.models.conversation import CustomerData

class TestConversationService:

    @pytest.fixture
    def mock_supabase_client(self):
        """Mocks the Supabase client."""
        mock_client = MagicMock()
        # Mock methods that might be called during ConversationService instantiation or basic ops
        mock_client.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {}
        return mock_client

    @pytest.fixture
    def mock_openai_engine(self):
        """Mocks the OpenAIEngine."""
        mock_engine = MagicMock()
        # Mock methods that might be called
        mock_engine.get_completion.return_value = "Mocked completion"
        return mock_engine

    @pytest.fixture
    def mock_elevenlabs_voice(self):
        """Mocks the ElevenLabsVoice service."""
        mock_voice = MagicMock()
        # Mock methods that might be called
        mock_voice.text_to_speech_stream.return_value = b"mocked_audio_stream"
        return mock_voice

    @pytest.fixture
    def mock_intent_analysis_service(self):
        """Mocks the IntentAnalysisService."""
        return MagicMock(spec=PersonalizationService) # spec PersonalizationService to include its methods

    @pytest.fixture
    def mock_personalization_service(self):
        """Mocks the PersonalizationService."""
        mock_service = MagicMock(spec=PersonalizationService)
        mock_service.generate_personalized_greeting.return_value = "Hola {customer_name}, bienvenido al programa {program_type}. Estilo: {communication_style}."
        mock_service.determine_communication_profile.return_value = "formal"
        return mock_service
        
    @pytest.fixture
    def conversation_service(
        self, 
        mock_supabase_client, 
        mock_openai_engine, 
        mock_elevenlabs_voice, 
        mock_personalization_service, # Use the more specific mock here
        mock_intent_analysis_service # Keep this if it's a different dependency
    ):
        """
        Provides a ConversationService instance with mocked dependencies.
        We patch the dependencies directly in the module where ConversationService looks for them.
        """
        with patch('src.services.conversation_service.supabase_client.get_client', return_value=mock_supabase_client):
            with patch('src.services.conversation_service.OpenAIEngine') as mock_engine_class:
                mock_engine_class.return_value = mock_openai_engine
                with patch('src.services.conversation_service.ElevenLabsVoice') as mock_voice_class:
                    mock_voice_class.return_value = mock_elevenlabs_voice
                    with patch('src.services.conversation_service.PersonalizationService') as mock_pers_class:
                        mock_pers_class.return_value = mock_personalization_service
                        with patch('src.services.conversation_service.IntentAnalysisService') as mock_intent_class: # If it's a dependency
                            mock_intent_class.return_value = mock_intent_analysis_service
                            # Instantiate the service; its dependencies will be the mocks
                            service = ConversationService()
                            return service

    def test_generate_greeting_prime_formal(self, conversation_service: ConversationService, mock_personalization_service: MagicMock):
        """
        Tests the _generate_greeting method for PRIME program with a formal communication style.
        """
        customer_data = CustomerData(
            name="Juan Ejemplo",
            email="juan.ejemplo@example.com",
            age=35,
            gender="male",
            occupation="Ingeniero",
            goals={"primary": "mejorar salud"}
        )
        program_type = "PRIME"

        # Configure the mock PersonalizationService specifically for this test case
        # The fixture already configures it, but we can be more specific if needed or override.
        # mock_personalization_service.determine_communication_profile.return_value = "formal"
        # mock_personalization_service.generate_personalized_greeting.return_value = "Saludos formales Juan Ejemplo, bienvenido a PRIME."

        # Call the private method (for testing purposes; consider if this is the best public API to test)
        greeting = conversation_service._generate_greeting(customer_data, program_type)

        # Assertions
        mock_personalization_service.determine_communication_profile.assert_called_once_with(customer_data)
        mock_personalization_service.generate_personalized_greeting.assert_called_once_with(
            name="Juan Ejemplo",
            program_type="PRIME",
            communication_style="formal", # This comes from the mock's return_value
            details=customer_data.model_dump() # or customer_data.dict() for Pydantic v1
        )
        
        # The greeting generated by _generate_greeting directly calls personalization_service.generate_personalized_greeting
        # So the return value of _generate_greeting IS the return value of the mocked generate_personalized_greeting
        expected_greeting = "Hola Juan Ejemplo, bienvenido al programa PRIME. Estilo: formal."
        assert greeting == expected_greeting
        
        # Verify that the mock was called as expected
        # call_args = mock_personalization_service.generate_personalized_greeting.call_args
        # assert call_args[1]['name'] == "Juan Ejemplo"
        # assert call_args[1]['program_type'] == "PRIME"
        # assert call_args[1]['communication_style'] == "formal"
        # assert call_args[1]['details'] == customer_data.model_dump()
