"""
Settings service layer.

Provides business logic for settings management operations.
"""
from app.models.settings import Settings
from app.storage.json_file import SingleValueStore


class SettingsService:
    """
    Service class for managing application settings.

    Handles reading and updating application settings,
    using JSON file storage backend.
    """

    def __init__(self, storage_path: str = "./data/settings.json"):
        """
        Initialize the SettingsService.

        Args:
            storage_path: Path to the settings storage file
        """
        self._store = SingleValueStore[Settings](
            filepath=storage_path,
            model_class=Settings
        )

    def get(self) -> Settings:
        """
        Get all current settings.

        Returns:
            Current application settings
        """
        settings = self._store.get()
        if settings is None:
            return Settings()
        return settings

    def update(self, settings_data: Settings) -> Settings:
        """
        Update all settings.

        Args:
            settings_data: New settings values

        Returns:
            Updated settings
        """
        return self._store.update(settings_data)

    def patch(self, settings_data: Settings) -> Settings:
        """
        Partially update settings.

        Args:
            settings_data: Settings values to update (only specified fields)

        Returns:
            Updated settings
        """
        current = self.get()
        update_data = settings_data.model_dump(exclude_unset=True)
        updated_data = current.model_dump()
        updated_data.update(update_data)
        updated_settings = Settings(**updated_data)
        return self._store.update(updated_settings)
