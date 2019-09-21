import io
import logging

import requests
from django.conf import settings
from django.core.files import File
from django.db import models
from django.db.models import options
from django.utils.timezone import now

logger = logging.getLogger(__name__)

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("settings_prefix",)


class ImageManager(models.Manager):
    def get_image(self):
        """
        Find an image that we can use. Returns None if
        the cache is empty.
        """
        images = self.filter(last_consumed__isnull=True).order_by("?")
        if images:
            image = images[0]
            image.last_consumed = now()
            image.save(update_fields=["last_consumed"])
            return image.image

        images = self.all().order_by("?")
        if images:
            image = images[0]
            image.last_consumed = now()
            image.save(update_fields=["last_consumed"])
            return image.image

        return None

    def _download_file(self, source, source_id, data_url):
        if self.filter(source=source, source_id=source_id):
            return False

        ext = data_url.split("?")[0].split(".")[-1]
        if ext == "zip":
            return False

        logger.debug(f"Fetching {data_url}")
        image = requests.get(data_url)
        filename = f"{source}-{source_id}.{ext}"
        self.create(
            source=source,
            source_id=source_id,
            image=File(io.BytesIO(image.content), name=filename),
        )

        return True

    def preload_images(self):
        """
        Add some images to the local cache if there's
        not a lot of unused.

        Can take some time to run.
        """
        prefix = f"WEEBLIFE_{self.model._meta.settings_prefix}"

        if len(self.all()) >= getattr(settings, f"{prefix}_CAP"):
            return

        for source in getattr(settings, f"{prefix}_ENABLED"):
            source_prefix = f"{prefix}_{source.upper()}"
            prefetch_count = getattr(settings, f"{source_prefix}_PREFETCH_COUNT")
            if (
                len(self.filter(last_consumed__isnull=True, source=source))
                >= prefetch_count
            ):
                continue

            fetched = 0
            if source == "danbooru":
                r = requests.get(
                    "https://danbooru.donmai.us/posts.json",
                    params={
                        "limit": "30",
                        "random": "true",
                        "tags": getattr(settings, f"{source_prefix}_TAGS"),
                    },
                )
                for entry in r.json():
                    source_id = str(entry["id"])
                    data_url = entry["file_url"]
                    if self._download_file(source, source_id, data_url):
                        fetched += 1

                    if fetched >= prefetch_count:
                        break

            elif source == "wallheaven":
                r = requests.get(
                    "https://wallhaven.cc/api/v1/search",
                    params={
                        "sorting": "random",
                        "q": getattr(settings, f"{source_prefix}_Q"),
                    },
                )
                for entry in r.json()["data"]:
                    source_id = entry["id"]
                    data_url = entry["path"]
                    if self._download_file(source, source_id, data_url):
                        fetched += 1

                    if fetched >= prefetch_count:
                        break

    def preload_and_get_image(self):
        """
        The easy way out when you're not in a hurry.
        """
        self.preload_images()
        return self.get_image()


class ImageAbstract(models.Model):
    source = models.CharField(max_length=100)
    source_id = models.CharField(max_length=100)

    last_consumed = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = ImageManager()

    class Meta:
        abstract = True
        unique_together = ("source", "source_id")


class LoadingAnimation(ImageAbstract):
    image = models.FileField(upload_to="weeblife_loading")

    class Meta(ImageAbstract.Meta):
        settings_prefix = "LOADING"


class Wallpaper(ImageAbstract):
    image = models.FileField(upload_to="weeblife_wallpaper")

    class Meta(ImageAbstract.Meta):
        settings_prefix = "WALLPAPER"
