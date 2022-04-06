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


## Important Concepts in This Section
1. Generally, throughout the site images are converted to jpeg automatically, so uploading large PNG files is best-practice for image uploads.
2. Renaming images you wish to replace is also best-practice to ensure that stale CDN cached images do not persist when you intend to replace them.
3. Audio and video file uploads are controlled via not only Wagtail and Django but also Nginx settings for max body size and request timeout, so very large videos will need a custom upload form that provides a chunked javascript uploader.

