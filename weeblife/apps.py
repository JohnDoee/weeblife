from django.apps import AppConfig
from django.conf import settings


class WeeblifeConfig(AppConfig):
    name = "weeblife"

    settings_prefix = "WEEBLIFE"
    default_settings = {
        "WALLPAPER_ENABLED": ["wallheaven", "danbooru"],
        "WALLPAPER_CAP": 1000,
        "WALLPAPER_WALLHEAVEN_Q": "",
        "WALLPAPER_WALLHEAVEN_PREFETCH_COUNT": 10,
        "WALLPAPER_DANBOORU_TAGS": "rating:safe wallpaper",
        "WALLPAPER_DANBOORU_PREFETCH_COUNT": 10,
        "LOADING_ENABLED": ["danbooru"],
        "LOADING_CAP": 1000,
        "LOADING_DANBOORU_TAGS": "rating:safe animated",
        "LOADING_DANBOORU_PREFETCH_COUNT": 10,
    }

    def ready(self):
        for k, v in self.default_settings.items():
            k = f"{self.settings_prefix}_{k}"
            if getattr(settings, k, None) is None:
                setattr(settings, k, v)
