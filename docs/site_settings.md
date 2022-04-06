# Site Settings

The `Settings` menu at the lower end of the main CMS menu contains site-wide settings, some of which you have specified already, but the rest are detailed here.

## Users and Groups

`Users` and `Groups` can be managed from their respective menus in the main site settings.  By default all registered users are placed into a `Customers` group to facilitate emailing to all registered users, particularly for drip emails.

As mentioned in the content authoring sections of this guide, the `Contributors` and `Authors` groups exist to provide selectable names for content authoring attribution on content pages.  These groups do not contain any special permissions within the CMS.

## Permissions

Permissions may be assigned to groups of users by selecting them in the `Groups` menu.  Note that by default, two-factor authentication is *required* for any user with access to the CMS admin, for security purposes.

With this in mind, if you give a user CMS admin access every page on the site will redirect them to a 2FA setup form until they set up 2FA.  You should probably warn them to set up 2FA on their own in their user profile beforehand to avoid this scenario.

If a user is using a phone app for 2FA and loses their phone, you can delete a user's 2FA devices for them by selecting `manage 2FA` under their name in the `Users` menu under the site settings.

## Collections

`Collections` are ways of categorizing things like documents and images into more manageable lists, since over time many hundreds or even thousands of images may be added to the site.

The usage of collections is optional.

See the Wagtail docs on collections for more detailed explanation on the usage of collections.

[https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/collections.html](https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/collections.html)

## Site Layouts

The `Layout` section of the site settings allows you to specify a favicon and global site logo for metadata purposes, as well as what items appear on your site's search result pages by default.

Additionally, as mentioned previously in this guide you may specify header and footer snippets in the site `Layout` settings that will apply to all search, subscribe, and user profile pages.

## Social Media

Links to `Social Media` accounts associated  with your brand may be specified in the `Social Media` site settings. These links are all optional, and serve two purposes.

1. They will be appended to a list in your JSON+LD SEO metadata to inform search engines that this site is the "same as" the `Social Media` profiles listed.
2. They will be selectable when creating button links on the site, so that you may quickly create buttons linking to your social media accounts without writing any code. You can combine icons from the Bootstrap icon library in the CSS "settings" of a button in a streamfield to create branded buttons for various social media sites.

See the bootstrap icon reference for button class names.

[https://icons.getbootstrap.com](https://icons.getbootstrap.com)

## Tracking

The `Tracking` section of the main site settings has a form field for you to input your Google Analytics ID if you choose to use it.  The javascript include for Google is conditionally included on the base site template and will be rendered if a GA ID is given.

There is a field for Google Tag Manager as well but by default this is not implemented, since it requires additional configuration on Google's end.

Refer to the template `website / templates / website / pages / base.html` in the head section of the HTML for how you might implement the tag manager code. It should be relatively simple to accomplish, with something like...

`{% if settings.website.AnalyticsSettings.ga_tag_manager_id and settings.website.AnalyticsSettings.ga_track_button_clicks %}`
...
`{% endif %}`

With the ellipses replaced by the provided Google script tag in the head section, and...

`{% if settings.website.AnalyticsSettings.ga_tag_manager_id and settings.website.AnalyticsSettings.ga_track_button_clicks %}`
...
`{% endif %}`

Again in the body of your base.html template, again with the provided Google iframe code replacing the ellipses.

## SEO

The `SEO` section of the main site settings contains site-wide JSON+LD schema settings for search engine purposes. 

Most options are self explanatory, but take care to correctly identify your Organization type, brand name, and main content type. These will affect the search engine metadata that appears on each page.  For the search engine metadata templates, see the `struct_data_` templates in `website / templates / website / includes`

If you need to specify additional JSON+LD schema data for your main page, you may do so here in the `additional organizational markup` box with the caveat that...

1. It must be in valid JSON+LD format (without curly brackets, it will go within the existing ones)
2. It must be properties of "Organization", see [https://schema.org](https://schema.org) for details.

## Google API

This setting is a single property for your Google Maps API key, if you wish to enable "places" support on Google Maps blocks.

## Cache

This is where you should go if you need to clear your site's page cache. Clicking the button purges the entire cache.

## Styleguide

The `Styleguide` is a Wagtail reference if you need to add any custom items to the CMS menu.  Of particular note are bundled icons that you may wish to use toward the bottom for custom menu items.

## Reports and Workflows

If you wish to use these functions, refer to the Wagtail documentation, they are unchanged from the CMS core in Rent Free Media as of the publishing of this guide.

