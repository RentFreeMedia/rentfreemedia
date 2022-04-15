# Paid Content

## The Subscribe Page

All user facing actions for the payment portion of this platform are available to the user via the `/subscribe/` page.  Othe templates within the payment app are just confirmation and redirect landing pages.

## Segments

`Segments` are the heart of Rent Free Media's support for paid subscriber content. If you have used other market segmentation libraries, you may be familiar with the functionality.

Essentially, users are assigned to a "tier" by rules matching their payment status. When a user requests a page that has a tier variant, they are given the version of the page that matches their tier silently.

For example, say you have a podcast where episode 3 is a preview of a paid episode. Behind the scenes, there may in fact be three versions of episode 3. You might have a "free" page that's a short preview of the episode, and a "tier 1" page that is the full episode for those who have subscribed to your first premium tier, and a "tier 2" page that is the full episode ad free for those who have subscribed to a higher premium tier.

Rules may be mixed to create complex page viewing experiences, but for the purposes of podcasts the "tier" rules are the most prevalent, so let's go through creating a simple premium tier.

**NOTE:** even if you used our Ansible scripts to install Rent Free Media, by default all Stripe data is running in "test mode", meaning that only test credit card numbers will work and no real money will be charged.  To set Stripe to "live" mode you must edit your `.env` file and set `DOSTRIPE_LIVE` to "True" instead of "False".  Before doing this, ensure that you have a valid webhook key specified for a valid webhook endpoint, and valid "live" stripe public and private keys specified in the `.env` file as well.

After any change to the `.env` file you need to restart your webserver for the change to take effect.

## Creating a Stripe Webhook Endpoint

You need to create an endpoint in your Stripe account that tells Stripe where to interact with your website backend to synchronize the database items. In your Stripe account dashboard, click on `Developers` in the upper right, and then click `Webhooks` on the left menu.  Next, click on  the `+ add endpoint` button, and specify an endpoint that looks like:

[https://mydomain.com/subscribe-events/](https://mydomain.com/subscribe-events/)

...replacing "mydomain.com" with your own domain name where Rent Free Media is installed. `/subscribe-events/` is the default listening address in Rent Free Media so should not be changed unless you know what you're doing and want to change the source code.

After you have created a webhook endpoint, click on it in the Stripe dashboard, and click `reveal` under "signing secret."  You will need to specify this key alongside your Stripe public and private keys in the `.env` file described in the `Install` section of this document, to authenticate webhook events sent by Stripe to your database.

If you are just adding the webhook secret to your `.env` file for the first time right now, you'll also need to restart your webserver for the change to take effect.

## Creating a Subscription Product

Let's create a subscription product with a price in your Stripe account that matches a product on your site. In your Stripe dashboard, click on `Products` in the menu at the top of the page, then click `Add Product`. 

Under `Product Information` you can name and describe your first subscription however you like, but you must specify additional metadata for Rent Free Media to identify this product as a subscription tier.  Under `Product Information`, click `additional options`.

Inside of `additional options` you'll see a `Metadata` option. Click the `+ add metadata` button, and specify a name of `tier` and a value of `1`. Rent Free Media assumes your tiers will be labeled numerically and identified by the name "tier", so only numeric values for the name "tier" are supported here on Rent Free Media.

Make sure to select "recurring" for the billing type and specify the price you wish to charge for your tier 1 subscription, as well as the subscription term, the most common option is "monthly", of course.

The configuration of your subscription tiers is largely up to you.  The only concepts that affect Rent Free Media are the subscription status, and the tier. If the subscrpition status is `active` and the user has a tier linked to a valid subscription product, the user will be granted access to items in that tier.  If you wish to have free trials or different billing terms other than monthly or any other such uncommon configuration, that is all up to you.

## Synchronization

After you create a Premium Tier, if your webhook is set up properly, the data in Stripe will sync to your local Rent Free Media installation in a minute or two. You can check this by clicking on the `Subscriptions` menu in the main CMS menu, and then clicking on `Products`. After the products have synchronized, your newly created subscription tier should appear.

Similarly, on the public facing pages of your site, the `/subscribe/` page should show the product available to logged in users as well.

## Creating a Subcription Segment

After creating your webhook endpoint and creating a subscription product, you can create the Rent Free Media `Segment` to match it, which will allow separation of content between paying users and free / public users.

Click on `Segments` in the main CMS menu, and select the `add segment` button.

Give the segment a name, it makes sense to name it after the tier here in the case of multiple tiers.  Let's call this segment "Tier 1". 

Defaults are correct for the next few choices, we want the status to be "enabled", the persistence to be unchecked (so that user subscription status is checked upon each request to the site), "match any" to be unchecked so that all rules must match for a user to match, and the "type" of segment to be dynamic, so that users may be added and removed from the tier automatically based on their payment status.

Next, we need to select the rule that will apply to these users.  Our choices here are toward the bottom, `Tier Equal` or `Tier Greater or Equal`. These are self explanatory and you can choose whichever you like depending on how you want to handle your subscription tiers.  For testing purposes let's just make one tier, and select `+ Add Tier Greater or Equal` to allow all users at or above our new "tier 1" to access paid content.

When you select the button to add the greater or equal rule, you will be presented with a dropdown box that lists your product tiers, you should be able to select the subscription product you created earlier.

After you've selected your subscription product, click save.

For further documentation on segments including custom rules, see the documentation for the segmentation library at:

[https://wagtail-personalisation.readthedocs.io/en/latest/](https://wagtail-personalisation.readthedocs.io/en/latest/)

Rules are relatively simple, all they require is set of criteria to test a user for that will return either "true" or "false".

## Creating Subscription Content

After creating a subscription tier and subscription segment to match it, you will notice some extra buttons alongside pages when you mouse-over them in your `/episodes/` page index, back in the page editing portion of the CMS.

The `variants` button will show you a pencil icon for pages that have a subscription tier variant, and a plus icon for pages that do not but can have a subscription tier variant.  Simply click the `+` under a page's variant button to add a premium tier version of that page.

Basically, what you will do for subscription content is create a preview page first that does not have the subscription tier content in it, but may have whatever other design you like, such as a short preview of a podcast episode or perhaps a paywall.  Then, after creating a `tier 1 variant` of that page from the page index, you will have a mirror image of that page that will contain the premium content users have paid for by subscribing to tier 1.  In the case of podcasts, premium authenticated RSS feeds are built for each paying user and shown to them in their personalized `/subscribe/` page, just as similar podcast subscription services do.  

A premium user's RSS feed will have a URL that contains an encoded version of their email address, and a secret key that is generated when they view the `/subscribe/` page that generates the link.  Navigating to that link will check their subscription tier status and if valid and active, allow their podcast app to download premium episodes using the credentials in their personalized URL.

Users will only be given a premium RSS link if their subscription to a tier exists, and is labeled as "active" by Stripe.  If any of the data used to generate the secret key changes the secret key will no longer work, so logically if their subscription status changes to anything except "active" their RSS link will no longer function, and they cannot get a new one from the `/subscribe/` page until their subscription tier status is returned to an "active" state.

For users of Rent Free Media selling written content similar to what they would provide on a service such as Substack, premium RSS feeds are generated for the written content as well that works in the same manner a podcast RSS feed works, if the user chooses to use a news reader app to access premium articles.

## Auditing Accounts and Users

You can audit the most common Stripe subscription data via the `Subscriptions` portion of the main CMS menu.  Note that most menu items are not editable, they are for display purposes only, as subscription data should not be changed locally, but rather changed on Stripe and sent to your database afterward.

The one exception is the `Media Downloads` auditor, which allows you to audit a user's downloads and optionally revoke their download links and RSS links if you suspect a user has shared their premium links publicly. Rent Free Media keeps count of how many times a user's RSS link has been used to download each premium content item.  

**READ THIS CAREFULLY**

If you suspect a user has shared their premium content feed / links publicly, you can revoke their current premium content link and force them to retrieve a new one from within the `Media Downloads` section, by selecting the user via the `edit` button under their name, and clicking the `reset user links` button.

**MULTIPLE DOWNLOADS ARE NOT AN AUTOMATIC INDICATION OF ILLEGAL SHARING OF LINKS**

Let's consider the average user, they may legitimately have a phone, a laptop, and an iPad all synchronized to the same Apple iCloud account.  In that case, they may legitimately download each episode three times.  Perhaps they have a streaming device like Amazon Alexa or Plex Media Server that can also subscribe to podcast feeds, which would bump their download count of each episode to five.

Perhaps users share download links with their spouse if both they and their partner listen to the same podcasts, which presumably you would want to allow as well.  That could raise their legitimate download count per episode to eight per episode if the spouse also has a phone, laptop, and iPad.

Reasonable leeway is the rule of thumb you should follow here.  If a user has three or five downloads per episode on a consistent basis, it's probably fine and all taking place within their household.  If a user has dozens or hundreds of downloads per episode, that's a good indicator that the user has shared their premium RSS link and the link should be revoked.

As the warning on the user audit page states, if you revoke a user's link, they will be notified by email.  The email template used to notify them is located at `users / templates / account / email / reset_message.txt`.  You can change the template if you wish to customize the message.

It should be noted that resetting the user's download link does not change their account or billing status, it just invalidates their RSS link by changing a parameter in their user profile, and thus forces them to obtain a new RSS link.

If you wish to ban a user from signing up for your subscription tiers, that should be handled via Stripe by cancelling their subscription and blocking their payment method.  See the Stripe documentation for instructions on how to do so.

## Review RSS Settings

This is a good point to add a reminder to review the RSS feed settings you created in your index page earlier in this guide.  There are relevant settings, such as whether or not preview episodes appear in your public RSS feed, and whether or not users are given "combined" feeds when they subscribe to a premium tier that allows them to unsubscribe the main public feed and receive everything they have access to in one single RSS link.

## Important Concepts in This Section

1. You must have at least one subscription product and your webhook endpoint properly configured in Stripe for Rent Free Media to function properly with paying users, so set Stripe up first.
2. Your subscription tier products must have "tier" metadata containing sequential numbers as values, as Rent Free Media uses these to calculate subscription tier access by applying "equal" and "greater or equal" rules.
3. `Segments` control the rules which allow users to receive paid content, so set up a segment after configuring your Stripe subscriptions and webhook endpoint.
4. You serve premium content by creating `variant` pages containing premium content matching your segment rules.
5. Stripe subscription data may be audited via the `Subscriptions` section of the main CMS menu, and user download counts may be audited (and optionally policed via revocation of RSS links) in the `Media Downloads` section of the `Subscriptions` menu.
6. Double check your RSS feed settings when creating subscription tiers and content, specifically in the case of podcasts, to make sure your preview episode visibility and combined feed settings are what you want them to be, before going "live" with your premium content.