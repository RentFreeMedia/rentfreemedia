# Comments

Rent Free Media includes the package `django-comment-dab` for AJAX user comments on pages you choose to include comments for, as well as upvote, downvote, and reply to other comments in a system that is as a whole very similar to the user experience of Reddit, for example.

There is a streamfield block called `user comments` available in the page body for each page which may contain user comments.  Including the `user comments` block will put comments on the page, and omitting it will exclude it from the page, no further configuration is required.

By default, to curtail automatic spam bots, the comment section will not allow a newly registered user to see or participate in comments.  They will receive a message that they must specify a username (which is not required on signup) in their profile and log in before viewing comments or commenting.

After a user has specified a username and logged in they will be allowed to see and participate.

## Controlling Comment Access

Using the principles explained in the previous section about paid content you could also optionally only allow comments for paying users, or only allow comments for logged-in users, by applying `Segment` rules to pages that have comment blocks in them.

For instance, you might specify a segment tier for "logged in" users, and only show the comment block on page variants that match "logged in" and "tier greater or equal" users, and thus encourage anonymous users to sign up at least, even if they don't pay for a premium tier, to see and participate in comments.  Then you could in turn market to them with promo codes to entice them to sign up for a premium teir at certain intervals with a drip email rule as described in the `Sending Emails` section.

The possibilities are fairly endless, since you also have access to custom rules which may be created for the segmentation library.

## Comment Moderation

The `Comments` section of the main CMS menu allows you to audit user comments and moderate them.

This functionality is not different from that provided by `django-comment-dab` by default so refer to their documentation for how to moderate your comments.

[https://django-comment-dab.readthedocs.io/en/latest/](https://django-comment-dab.readthedocs.io/en/latest/)

## Comment Customization

`django-comment-dab` uses Boostrap for styling by default, as Rent Free Media's templates do, so changes to your bootstrap css file will automatically apply to django-comment-dab styling as well.  If you choose to use a different CSS framework you will need to change the comment templates to match, or alternatively use the `django-comment-dab` API to return JSON data for comments and render them outside of the scope of HTML and CSS, that is up to you if you choose to perform heavy customization of your Rent Free Media installation's UI and templates.

