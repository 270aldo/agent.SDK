from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = AppSettings()

# Optional: Add a way to log loaded settings for verification, especially in debug mode.
# This should be done carefully to avoid logging sensitive keys directly in production.
if settings.DEBUG:
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("--- Application Settings Loaded ---")
    logger.debug(f"OpenAI API Key: {'*' * (len(settings.OPENAI_API_KEY) - 4) + settings.OPENAI_API_KEY[-4:] if settings.OPENAI_API_KEY else 'Not set'}")
    logger.debug(f"ElevenLabs API Key: {'*' * (len(settings.ELEVENLABS_API_KEY) - 4) + settings.ELEVENLABS_API_KEY[-4:] if settings.ELEVENLABS_API_KEY else 'Not set'}")
    logger.debug(f"Supabase URL: {settings.SUPABASE_URL}")
    logger.debug(f"Supabase Anon Key: {'*' * (len(settings.SUPABASE_ANON_KEY) - 4) + settings.SUPABASE_ANON_KEY[-4:] if settings.SUPABASE_ANON_KEY else 'Not set'}")
    logger.debug(f"Supabase Service Role Key: {'*' * (len(settings.SUPABASE_SERVICE_ROLE_KEY) - 4) + settings.SUPABASE_SERVICE_ROLE_KEY[-4:] if settings.SUPABASE_SERVICE_ROLE_KEY else 'Not set'}")
    logger.debug(f"Log Level: {settings.LOG_LEVEL}")
    logger.debug(f"Debug Mode: {settings.DEBUG}")
    logger.debug("-----------------------------------")
