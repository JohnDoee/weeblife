weeblife
==============

Weeblife is a Django App that allows you to get a random wallpaper or loading animation.

Usage
-----

First, add `weeblife` to `INSTALLED_APPS`.

.. code-block:: python

    from weeblife import Wallpaper

    # Download some images so we have some ready. This command is slow
    Wallpaper.objects.preload_images()

    # Returns a Django File object that you can use to serve a random image.
    image = Wallpaper.objects.get_image()


Remember to run `preload_images` periodically to fetch new images.
To get a loading animation use `LoadingAnimation`, the API is the same as for `Wallpaper`.

License
-------

MIT, see LICENSE