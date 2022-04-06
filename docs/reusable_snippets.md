# Snippets

Snippets are fragments of pages such as paywalls, headers, and footers which may be re-used throughout the site on multiple pages. They are stored independently of pages in the database, but allow the editor to create page-like streamfield content within them.

Snippets do not have "preview" functionality like pages since they are not attached to a page by default, but can be previewed by creating a draft page, attaching a snippet to that draft page, and then previewing the page.

## Content Walls

Paywalls are an obvious use case for snippets. In Rentfree, editors may create paywalls as snippets and then attach them to any number of pages after the fact. 

## Headers and Footers

Header and footer menus may also be created as snippets. The editing experience is identical to the streamfield that you learned about previously when editing a page, but for extra CSS options such as specification of rows and columns to better control the layout of the resulting header and footer.

Headers and footers may be specified in two different location types after they have been created.

1. In the main CMS `Settings`, under `Layout`, default header and footer options may be specified for pages which do not exist in Wagtail.  For example the user registration and user profile pages and the payment pages are stock Django views, not Wagtail pages / views.  Defining a default header and footer snippet for those page types in settings / layout will apply the selected footer and header to those pages.
2. Wagtail pages can have a header and footer selected on a per-page basis, in the page editor's `Layout` tab.


## Important Concepts in This Section


1. Snippets are for creating re-usable page components like paywalls, headers, and footers.
2. There is no built-in preview functionality when editing snippets, but they can be previewed by attaching them to a page draft, and then previewing the page draft in another browser tab.
3. Headers and footers can be specified per-page on Wagtail pages in the `Layout` tab, and in the main site settings under `Layout` for page categories that aren't rendered by Wagtail, such as user profile pages and payment pages.

For further documentation on snippets, see the Wagtail core docs:

[https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/snippets.html](https://docs.wagtail.org/en/stable/editor_manual/documents_images_snippets/snippets.html)