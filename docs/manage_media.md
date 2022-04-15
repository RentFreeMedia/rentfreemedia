# Images and Media

Wagtail has the ability to not only host but also automatically manipulate images "on the fly" in templates.  

## Image Conversions

Generally, all of the provided default templates included with Rent Free Media convert images to jpegs, so if you wish to upload large PNG files rather than pre-convert them to smaller web-friendly versions that's not only okay, but encouraged for the purpose of easy management.

The [Wagtail Docs](https://docs.wagtail.org/en/stable/topics/images.html) have a very well-written section on manipulating images in templates, so we'll not simply repeat them here but rather suggest that you read those if you need to adjust the output of the images in the default templates.

## Image Naming

Most people who host this project will use an external CDN or at least another S3 storage bucket for public media (image) hosting. A benefit of such services is their cache, that can serve content without hitting the source file every time to check for a new image rendition.

A gotcha with that benefit is that re-generating an image won't necessarily serve it right away, so you will either need to clear your CDN's cache when you need to do so or, alternatively, rename images when you need to replace them.

If you need to replace an image in a page or RSS feed, renaming it will force the upstream cache from whatever CDN and image storage solution you use to get the new filename, so renaming is a good practice to get into with image replacements.  If you rename, there's no reason to worry with clearing your upstream CDN's cache, the cached versions of stale images will eventually expire on their own.

You should also take care to avoid uploading multiple images with spaces and other such incompatible characters that have very similar names. The CMS can handle them and sanitize the filenames, but depending on the length of the filenames it may truncate the filenames at the spaces.

In short, explicitly name them, don't make a habit of uploading a dozen images that all begin with "instagram " (note the space), lest the CMS split the filename at the space due to filename length considerations and confuse one with another.

## Audio and Video

For content pages, audio and video can either be uploaded and hosted directly (required for paid podcast content that will appear in an RSS feed, optional for public content or content hosted only on the website), or linked to remotely. For remote content, Youtube and Vimeo are supported in addition to linking directly to video and audio files. 

Uploaded content can be managed just like images via the `Media` section of the main CMS menu.  If you used the provided Ansible deployment scripts, the maximum upload size was set to 300 megabytes with a form submission time of 300 seconds. This should allow for any podcast content, but may need to be adjusted for larger video files.  There are three settings which control this limitation:

1. `client_max_body_size 300M;` in /etc/nginx/sites-available/main_site.conf
2. `proxy_read_timeout 300s;` in /etc/nginx/sites-available/main_site.conf
3. `ExecStart=%h/.local/bin/gunicorn website.wsgi --timeout 300 (...)` in /home/rentfree/.config/systemd/user/gunicorn.service

More optimally, a custom upload form could be provided that allows for chunked uploads of large video files, which would bypass the request body size and timeout limits present in this section. The media plugin that this distribution uses supports custom forms, documentation is available at:

[https://github.com/torchbox/wagtailmedia](https://github.com/torchbox/wagtailmedia)

Your storage for premium content must be compatible with [django-storages](https://django-storages.readthedocs.io/en/latest/) or, you must provide your own storage library and settings, one or the other. The default storage classes are compatible with Digital Ocean and are specified in `rentfree / custom_storages.py` if you need to change any options. There's a storage class for static files, a storage class for public media, and a storage class for premium / private media. They are named accordingly. The primary difference between them is that the premium / private bucket is set to not use any CDN-type URL, and is set to private for all objects.

Premium media embedded in pages with the provided javascript player uses temporary signed URLs from the storage backend, whereas RSS feed premium media items use X-Sendfile URLs.  RSS feed X-Sendfile media downloads are tracked in the `Subscriptions` menu in the CMS, the embedded player in site pages does not register a download for playing premium media via the embedded player. The idea behind this design is that users sharing their feed with others is the most common form of illegal sharing of premium content, whereas it's less likely that a user would give their username and password for a site with billing information on it to another person or group of people.


## Important Concepts in This Section
1. Generally, throughout the site images are converted to jpeg automatically, so uploading large PNG files is best-practice for image uploads.
2. Renaming images you wish to replace is also best-practice to ensure that stale CDN cached images do not persist when you intend to replace them.
3. Audio and video file uploads are controlled via not only Wagtail and Django but also Nginx settings for max body size and request timeout, so very large videos will need a custom upload form that provides a chunked javascript uploader.

