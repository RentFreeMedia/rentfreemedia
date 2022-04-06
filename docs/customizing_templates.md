# HTML Templates

Rent Free Media includes Bootstrap templates by default, and includes a means of customizing templates selectively in the database, so that you may retain a "stock" installation for easy upgrades while also changing templates you wish to change.

Storing templates in the database also makes migration from server to server or replication in the case of server redundancy easier.

In `websites / settings / prod.py` in the `TEMPLATES` section of the Django settings, you'll notice `dbtemplates.loader.Loader` commented out.  After your initial database migration on a new site, if you wish to enable database templates, simply uncomment this line by removing the `#` and save the `prod.py` file, run `python3 manage.py migrate` via your server's shell in the `/ home / rentfree / rentfree` folder, and restart your webserver.  After doing so the `HTML Templates` option should appear in the main CMS menu.

## Template Override

To customize a particular template, first click on `HTML Templates` in the main CMS menu, and then click `add template`.

If you save a template that already exists without any content, the existing template on the disk will be copied to the database template, and the database template will override the template on disk, so always do that first when customizing templates.

For example, if you wish to override the template for the "pagelist" streamfield block, you would click `add template` and type the relative path to that template, `website/blocks/pagelist_block.html`, while leaving the content box blank.  

Then, save the template and re-open it, and you should see the content box populated with the template defaults, copied from the template on the server disk. At this point you can modify the template within the CMS as needed and the template from the CMS database will override the template on the disk.

If you make a catastrophic mistake and / or need to restore the default template, simply delete the template from the `HTML Templates` section and the template on the server disk will return to the top of the precedence list and be served in place of the broken database template.

With all of this in mind, it would probably be a good idea to save a document externally that contains your HTML Template changes, so that you can restore to a working state if you make a mistake.

## Template Logic

Django templates are very similar to Jekyll templates if you have ever used, for example, Github pages or the Jekyll static site generator by itself, and also very similar to Shopify templates if you've ever set up Shopify pages.

You can not only render items from the database but also include logic at the template level, as we briefly explained in the `Sending Email` section of this guide.

Refer to the Django template docs and Wagtail template docs for detailed template documentation.

Before you decide to create an entirely new UI for a Rent Free Media site to replace all of the stock templates, consider the fact that you can go a very long way toward a completely custom site with only custom headers and footers, a custom bootstrap css build, and a few custom HTML templates.

There are over 110 HTML templates in the main `website` app of Rent Free Media. This isn't counting the user profile templates and the payment app templates for Stripe subscriptions. However, most of them are simple containers with placeholders for options you specify in the CMS and not specific to a particular style or design. For example, on the [Dubious Podcast](https://dubiouspod.com) site as a "mostly stock" example, we only have a custom bootstrap css and seven custom HTML templates, we are otherwise completely stock in terms of Rent Free Media templates.  Our headers and footers are defined as snippets in the database as well.

Most of a website's appearance is in the menus, stylesheet, and basic layout, all of which can be accomplished on Rent Free Media sites without complete replacement of all of the HTML templates in most cases, unless you really want to replace the entire UI with something completely custom.

If you do, you should check out guides such as Kalob Taulien's excellent "headless Wagtail" tutorial for how to proceed.

[https://learnwagtail.com/tutorials/how-to-enable-the-v2-api-to-create-a-headless-cms/](https://learnwagtail.com/tutorials/how-to-enable-the-v2-api-to-create-a-headless-cms/)

Also, please consult the Django and Wagtail documentation for further template customization tutorials if you are unfamiliar with Django templates entirely.

[https://docs.djangoproject.com/en/stable/topics/templates/](https://docs.djangoproject.com/en/stable/topics/templates/)

[https://docs.wagtail.org/en/stable/topics/writing_templates.html](https://docs.wagtail.org/en/stable/topics/writing_templates.html)

[https://docs.wagtail.org/en/stable/topics/images.html](https://docs.wagtail.org/en/stable/topics/images.html)