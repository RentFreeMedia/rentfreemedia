# Sending Email

Rent Free Media has powerful email sending capability which allows you to not only manually email single users or groups of users, but also email marketing promotions to users by rules which parse user profile data, and in turn send personalized email to users based on templates.

It is highly recommended to use an API based email provider such as Mailgun, Amazon AWS SES, Mailjet, or Sendgrid.  When sending large amounts of email, performance becomes a concern.

If you used our Ansible scripts to deploy your site on Digital Ocean, or if you deployed Rent Free Media yourself and set up email to send via Unix / Linux cron, you will be checking for queued email and sending them out once per minute.  An SMTP based email setup will connect, send, disconnect, and reconnect for every single outgoing email, which is rather slow. Logically, if you have more emails to send than can be processed via SMTP in one minute, your server will fall behind in its own email queue, and a newly registered user or new paying subscriber might not get their confirmation email right away, as an example of the problems this could create.

The requirements for Rent Free Media specify [Django Anymail](https://github.com/anymail/django-anymail) as a dependency so the answer to this problem will already be installed. Consult the Anymail docs for your API email service to configure Anymail for sending via API. Using an API based email provider you will be able to send emails in batches, which should alleviate the performance concern for up to tens of thousands of users.  If you get into hundreds of thousands or millions of users, you will be into custom deployment solution territory anyway, so that is a bridge to cross when your audience size reaches such levels.

## Email Templates

Rent Free Media uses a slightly customized version of [Django Post Office](https://github.com/ui/django-post_office) to send email by template.  Our fork of Post Office is modified to include support for sending mail to groups of users, user data context in templated email sent to groups of users, per-user unsubscribe links in any mail sent via a template, and automatic omission of users who have unsubscribed from mail sent via a template.

Under the `Email` portion of the main CMS menu you'll notice the first option is `Email Templates`. These allow you to send one message to an unlimited number of users by group (all users who register via the public facing sign up forms are put into a "customers" group by default for example), and personalize things such as the person's name in each email that is sent.

Lets make an email template.

Step 1. Click on the `Email` menu item, then click `Email Templates`. When you arrive at the empty template list, click the `Add Email Template` button. In the editor, you must first specify a name for the template, lets call this one "test template" for demonstration purposes.

Step 2. The description is optional, its only purpose is to give you a field to search in the future when you find yourself with hundreds of email templates and need to find a particular one.  Put "test" for this description for now.

Step 3. All that remain in your email template are the `Subject`, and one or both of `HTML Content` and `Text Content`. These boxes are what they suggest. You can send plain text, or HTML, or both.

You'll notice that the usubscribe link required to be in the email body is already included in the email template, so don't remove it or you will be out of compliance for sending bulk email without including a means of unsubscribing.  Add your email content above the unsubscribe link(s).

*(Tip: A useful way to generate nice looking email templates is the open source project GrapesJS. There is a demo of the email template builder on their website that you can use for free to make email templates, at [https://grapesjs.com/demo-newsletter-editor.html](https://grapesjs.com/demo-newsletter-editor.html))*

You can personalize email rendering by including user data template variables. A user's main profile context (minus password and session data) is included in the email template context by default.  `Context` in the case of a Django / Wagtail application like Rent Free Media means the data available from the database for you to use for a particular view or function.

Lets take a look at the user context from an email that has already been sent and see how to use it.



```
{
    "id": 2,
    "last_login": "2022-03-03T18:21:26.187956Z",
    "is_superuser": true,
    "first_name": "Sandra",
    "last_name": "",
    "is_staff": false,
    "is_active": true,
    "date_joined": "2022-03-03T18:15:12.215513Z",
    "user_name": "",
    "email": "sandra@email.com",
    "is_mailsubscribed": true,
    "is_paysubscribed": 1,
    "paysubscribe_changed": "2022-03-05T16:05:16.182439Z",
    "is_smssubscribed": false,
    "is_newuserprofile": true,
    "stripe_customer": 14,
    "stripe_subscription": 14,
    "stripe_paymentmethod": 17,
    "url": "",
    "download_resets": 0,
    "unsubscribe": "domain.com/unsubscribe/asdf1234/1234asdf/"
}
```

In this case we can see that we have a user named Sandra, whose email is sandra@email.com. She is subscribed to email alerts and offers from us (`is_mailsubscribed`: `true`) and is also a premium content subscriber at tier 1 (`is_paysubscribed`: `1`). 

We can use these little bits of data to personalize the email template that will be sent to each user.

For example, if we put `Dear {{ first_name }},` in the place of where we might put the user's name, such as in the first line of an email reading "Dear Sandra," the email will be personalized for *every user that receives an email sent by this template*. A user named John would recieve "Dear John," for example.

Beyond this simple example, you can also employ logic in the template rendering to customize the content.

For example, if we wanted to send an email to all email subscribed users about new content and selectively offer promo codes based on subscription tier, we could do something like the following...

```
{% if is_paysubscribed == 1 %}
Thanks for your subscription to our content! 
Here is a sneak peek at the latest episodes we are working on...

Did you know that if you upgrade to tier 2, you could also get XYZ?  
As a token of our appreciation, here is a promo code.

MY50OFFPROMO

Enter it at checkout to get 50% off a subscription upgrade.

{% elif is_paysubscribed >= 2 %}

Thanks for your subscription to our content! 
Here is a sneak peek at the latest episodes we are working on...

{% else %}

Here is a sneak peek at the latest episodes we are working on...

Did you know that we have subscriber only content?
If you are curious, sign up for a premium subscription!
Use this code at checkout to get 25% off of any subscription tier:

MY25OFFPROMO
{% endif %}
```

Lets examine what the above email would do...

Firstly, it would check to see `if` the user `is_paysubscribed` exactly equal to (`==`) the lowest tier, tier number 1 (`{% if is_paysubscribed == 1 %}`).  If so, it would include a thanks for their subscription, the sneak peak at future content, and a promo to offer the user an upgrade to tier 2 or higher at half price, in the form of a coupon code that they could apply at checkout when they upgrade.

Else, if the user is already subscribed at a tier greater than or equal to 2 (`{% elif is_paysubscribed >= 2 %}`), the promo code offer would be exlcuded, and the user would only get the sentence about "thanks for subscribing to our content, here's the sneak peek."

Else (`{% else %}`) if the user is a subscriber of neither tier 1, nor greater than or higher than tier 2, omit the "thanks for subscribing to our content" sentence, and instead send the user a 25% off promo coupon good for *any* subscription tier, since we can presume that if they're not tier 1, nor greater than or equal to tier 2, they do not have a premium subscription at all.

This email could then be sent to all email subscription enabled users, and each one would get content and coupon codes personalized based on their subscription tier. For more examples on how to use template logic, see the [Django documentation](https://docs.djangoproject.com/en/stable/).

Back to our test template. Type a subject, some plain text or HTML content, and start the email by addressing it to Dear `{{ first_name }}` as in our previous example, and save the template.

## The Send Emails Queue

`Send Emails` is where you go to send email via the templates you have created, or just to send a "one off" email to a user or group of users.

It should be noted that unless you send via a template, which has the pre-appended unsubscribe link, users *WILL NOT GET* an email with an unsubscribe link.  Consider this when sending one-off emails without a template, to avoid falling out of compliance in terms of marketing email rules. The short answer to the situation regarding unsubscribe links is "if in doubt make a template, even for a one-time email."

Click on `Email` in the main CMS menu and then `Send Emails` to get to the mail queue. From here, click `Add Email` to create a new email.

Step 1. The `Email from` field should already be filled with the default email you have provided in your main site settings.

Step 2. You can choose either a single recipient by typing the email address, a comma separated list of email addresses, or a group to send the email to. Lets choose Moderators from the group email list for this example to send a test email to everyone with access to the CMS admin section, so leave the `Email to` line blank and select `Moderators` from the group list.

Step 3. Select the template you created in the previous step as the template to use for this email.

Step 4. The `status` field changes based on the email's send status, but can also be manually specified to send email by selecing `queued`, so select that option now for this email to send it out in the next batch.

You don't need to specify priority if you don't want to, but if you need to do so for performance reasons as mentioned at the top of this guide, the option exists. 

`Scheduled sending time` is hopefully self explanatory. If you specify a date and time, the mail will be sent at that date and time, otherwise a queued mail will go out in the next batch.


After filling in these options click `save` to save the email queue addition, and your email will be sent with the next outgoing batch (or at the scheduled time if you selected one).

If you are using our Ansible scripts to deploy to Digital Ocean, as mentioned at the top of this section emails will be sent every minute via cron.  If you are running the dev version of this project locally and haven't set cron to send mail, you can manually send the mail queue from the command line via the `send_queued_mail` command.

From the rentfree folder you created in the install section of this guide, in your terminal window:

`python3 manage.py send_queued_mail`

You should see an output like the following after running this command:

```
[INFO]2022-03-21 PID 137337: Acquired lock for sending queued emails at /tmp/post_office.lock
Acquired lock for sending queued emails at /tmp/post_office.lock
[INFO]2022-03-21 PID 137337: Started sending 1 emails with 1 processes.
Started sending 1 emails with 1 processes.
[INFO]2022-03-21 PID 137337: 1 emails attempted, 1 sent, 0 failed, 0 requeued

1 emails attempted, 1 sent, 0 failed, 0 requeued
```

...and shortly thereafter you should receive the email you sent if you put a valid email address in when you created your admin account in the install guide.

## Drip Email

Rent Free Media also has a second, more powerful way to send rule-based emails to your users.  `Drip Email` allows you to specify any number of rules to send email to users by, including all data *related to* the main user field in the database, and most importantly, only send each drip email to each user one time.

By using drip email, you could have a whole marketing plan's worth of emails pre-written for users based on arbitrary criteria, and they would all send only once to each user and only at the time which all of the rules in an email "pass."

Lets create a drip email as an example.

Step 1. Select `Email`, and then `Drop Email` from the main CMS menu.

Step 2. Click on `Add Drip`

Step 3. Give the drip email a name, lets call this one "test drip".

Step 4, Leave `enabled` unchecked, so that we can test the email before it sends.

Step 5. `From email` should already be filled based on the admin email you supplied in your main site settings.

Step 6. `From email name` is optional, it will be appended as the "from email" user's common name, for instance "Mysite.com Admin" would make sense.

Step 7. The `subject template` and `body template` are exactly like their counterparts in the previous section.  You can use not only plain text or HTML, but also user variables such as `{{ first_name }}` to fill the user's real first name.  Compose some text, and as in the previous example address it by providing a first line of "Dear {{ first_name }},"

Step 8. At this point we must define our rules.  This is very similar to the code-based rules we used as an example in the prior section, but in this case there is a menu to define them, and there are more user data fields available to you.  All related database fields specific to users are present for you to check rules against.

You'll notice that one rule is already pre-filled, our unsubscribe check.  Lets break down what each option means.

`Method type` defines whether the rule includes users (filter) or excludes them (exclude). We want to include users who are mail subscribed, so leave this as "filter."

`Field name` is the database field you wish to check for the data you are going to test for the rule, in this case "is_mailsubscribed" to make sure the user has not unsubscribed from email alerts.

`Lookup type` is how we are going to compare the data, as you can see you have more options here, but we want users who are "exactly" 1, or the boolean true/false equivalent of `true` for their mail subscription status.

Lastly, `rule type` defines this rule's relation *to the other rules*. In this case, we want this rule to be additive, so we select "and" whereas if you wanted to compare *multiple rules* you could select "or" instead. Remember how Authors and Contributors were able to have multiple values in the podcast content page editor in the previous section? Drip rules work exactly the same way. You can simply add another rule, define either `and` or `or` as the rule type, and have a theoretically infinte number of filter rules applied to each individual email template.

*(These are powerful filtering features and it is highly recommended that whomever writes your drip email templates and rules read the documentation at [https://django-drip-campaigns.readthedocs.io/en/latest/](https://django-drip-campaigns.readthedocs.io/en/latest/) and [https://django-drip.readthedocs.io/en/latest/](https://django-drip.readthedocs.io/en/latest/). In particular, the date/time filters are quite useful for marketing email purposes.)*

Finally, save the drip email, and back on the previous page, if you hover your mouse over the drip email you will see a button labeled `inspect`.  This is the *most* useful feature of this method of sending mail, clicking on inspect will show you the emails, hypothetically, that would have been sent 3 days prior to today through 7 days after today.  It is highly recommended that you save your drip emails not `enabled` and run this test to see if they match the users you expect them to match, before enabling them.

If you're satisfied that the email is going to be sent to the proper users, you can re-edit the drip email you created and change the status to `enabled` to set the email to send on the next scheduled sending time.

Unlike account and invoice emails which need to be sent as quickly as possible drip emails are designed with marketing in mind, so do not need to be sent as regularly.  If you are using our Ansible scripts to deploy to Digital Ocean, a cron job was created to send drip emails once per week on Thursdays, by default. You may want to check the time on the rentfree user's crontab to tweak the time of day that they send to your liking, by logging into your server's console and running...

`crontab -e`

...as your rentfree user.

The command to send drip email manually, and the one that will be specified in your crontab if you used our Ansible scripts is (again from your rentfree user's "rentfree" folder)...

`python3 manage.py send_drips`

## Email Logs

The drip email functionality ensures that each user only receives a particular email one time by checking against its log when sending emails.  *YOU SHOULD NEVER DELETE THE DRIP EMAIL LOGS* for this reason.

The primary `Send Emails` queue from the first half of this part of the guide on the other hand will quickly become quite large, since you are sending not only any marketing emails you create with its templates but also registration confirmations, password change emails to users who need to reset their passwords, subscription confirmations, etc.  With that in mind, there is a cron job created by our Ansible scripts to purge the queue of old emails every night.

The command is...

`python3 manage.py cleanup_mail -d 30 --delete-attachments`

Predictably, "-d 30" stands for "days 30" and --delete-attahcments deletes orphaned email attachments. So if you run it every night, you'll have a constant log of 30 days of emails in case you need to retrieve one for whatever reason.

## Important Concepts in This Section


1. `Emails` in Rent Free Media may be sent from the CMS admin two ways, either manually by template and adding them to a queue to be sent to individual users or a group, or by `Drip Mail` which are rule-based primarily designed for marketing purposes.
2. User context is available in both email template types to personalize emails sent to each user via a template.
3. Unsubscribe links are automatically generated in email templates and you should be careful not to delete them, lest you forget to include them and fall out of compliance with email marketing laws and platform terms of service.
4. The `Send Emails` log should be cleaned out via a daily cron job that deletes email older than a certain number of days to avoid over-filling your database with email logs, while you should **NEVER** delete any of the `Drip Email Logs`.
5. People can receive any email you specify in the `Send Emails` queue, but by design each user will only receive each drip email once.

Next, we will go over uploading images and media.