[![Documentation Status](https://readthedocs.org/projects/rentfreemedia/badge/?version=latest)](https://rentfreemedia.readthedocs.io/en/latest/?badge=latest)

## Rent Free Media

RentFree Media is a media distribution framework built on Django and Wagtail. With it you can publish either public or premium / subscription-based content similar to the features provided in services such as Patreon, Apple Podcasts, and Substack.

## Need Help? Have Questions?

Feel free to post a [discussion](https://github.com/RentFreeMedia/rentfreemedia/discussions) for questions or an [issue](https://github.com/RentFreeMedia/rentfreemedia/issues) if you have trouble, contact info is also available in my git profile if you'd like to hire me to help with deployment or customization, or just talk for a few minutes about how you might use the code, I'm happy to help!

When ready to give this all a try, please [read the docs](https://rentfreemedia.readthedocs.io/) for instructions on its usage.

### Summary of Features

* Your media distribution tools also become your brand's website. Media objects can also be embedded on your website's pages if you like.
* Click-able block-level CSS styling: add CSS classes to individual template blocks without getting into the code for minor style adjustments.
* The base templates are plain ole HTML and CSS. No JavaScript is required to customize your site's design, unless you want there to be.
* Base templates use [Bootstrap 5](https://getbootstrap.com/docs/5.0/getting-started/introduction/). You can customize your whole site design with a custom header, custom footer, and `bootstrap.css` modifications.
* Dismissable content walls / "paywalls" if you choose to employ them, defined at the individual page level.
* Full text site-wide search, enabled by default.
* Customize ***anything*** by user tier. Subscription tier filters are included out of the box, and custom tier filters can be defined in python code and mixed, matched, or combined in any way you see fit.
* Premium authenticated RSS feeds if you are publishing articles as one would do on Substack, or podcasts / video casts as one would do on Patreon, with secure links to paid subscription content.
* RSS feeds for podcasts and video casts are configurable for most use cases. Define serial or episode-type feeds. Selectively include your promos of paid episodes... or not. Host your public episodes remotely... or not. Include your public feed combined with your paid feed for paying users... or not.
* Write your notes and / or articles in WYSIWYG rich text or Markdown, your choice. Our customized Markdown library produces [Chicago-style footnotes](https://www.chicagomanualofstyle.org/tools_citationguide.html) which work in iTunes.
* Premium downloads are audit-able and those audits action-able. Revoke a publicly posted premium link based on download stats with a single click in the admin panel.
* Rule-based email marketing tools, send templated email to your users by any user data you can define, without writing any code. 'Unsubscribe' links are handled automatically.
* Stripe integration for subscription payments tied to premium content, including Stripe features like promo / coupon codes.
* AJAX user comments, along with moderation tools, by whatever rules you choose.  Host comments in your own database for only paying users, or only signed-up users, or everyone in the world.
* Professional content collaboration tools. You can have writers who need an editor's permission to publish, and editors who need an admin's permission to publish... or none of the above... or some of the above... configure your permissions how you like them.
* Two factor authentication, available to all users and enforceable on anyone with admin access if you choose.
* Google analytics integration, down to the link-level. Define tracked links and buttons right in the page editor, no need to write code.
* [JSON+LD](https://json-ld.org/) SEO schema integration done right, out of the box, automatically.  Enable and define the settings and they "just work."
* A cache based on [wagtail-cache](https://docs.coderedcorp.com/wagtail-cache/) with support for all Django cache backends. Use the local disk, or Redis, or Postgres, or Memcached if you prefer. All unauthenticated requests are cached out of the box, so Google, Apple, and anonymous users won't beat up your database.

### Thanks
 
Particular thanks not only to the Wagtail core developers and the developers of all of the third party libraries we use, but also specifically to [CodeRedCorp](https://www.coderedcorp.com) for open-sourcing their Wagtail projects. It is from their examples that most of the base-level page design of this project is derived. And also particularly to [Kalob Taulien](https://github.com/KalobTaulien) for his wonderful Wagtail development tutorials. 

### Things you will need

1. A web host (virtual server or bare metal)
2. A Stripe account, for payment processing
3. An email service for invoices, user registration confirmation, and other such typical things
4. A storage service such as Digital Ocean Spaces, AWS S3, Backblaze, etc for storing your content
5. A laptop / desktop to run the deployment scripts on

That's it!  After filling in the blanks you will be *your own* premium media distribution service, without the (egregious) fees of the above mentioned publishing services.

### Deployment

Serving content to paying customers is not trivial to do securely and robustly. Your own Nginx installation is required to do this, as each request for premium content must first be authenticated, and then fetched from storage and routed back to the user. We cache media files on the server and thus the storage service is "just storage" for the Nginx reverse proxy in front of Django to serve end users through.  Media files are cached by Nginx on the server's local disk to minimize traffic between the front end and the back end. 

Ansible scripts are provided in the ansible folder for automated deployment to Digital Ocean, which as a cloud service is particularly well suited to host this project because of their generous download bandwidth pricing.

If you choose to deploy the project manually, refer to the Ansible templates (`ansible / includes / webserver` and `ansible / includes / systemd`) for Nginx and Gunicorn configuration, sans the Ansible variables. 

Let's consider the math in terms of a Digital Ocean deployment:

Presume that you have 20,000 paying customers who download your weekly (4 times a month) premium-user podcast which weighs in at 100mb for a one hour long MP3 file.  Presume also that on average, each of your 20,000 paying customers downloads the episodes on three different devices.

20,000 x 3 x 4 = 240,000 downloads a month

240,000 x 100mb = 24,000,000 megabytes per month downloaded

24,000,000 mb / 1024 = 23,437 gigabytes

23,437 x $0.01 per gigabyte = $234.38

Even if we don't manage to convert the world with this project, we would hope to impress upon people that serving media is not worth 10% or 18% or 25% or 30% of your gross receipts, as other media distribution "services" seem to think by virtue of their pricing. The cloud service seems to think that it's worth $0.01 per gigabyte, and you should be looking to pay accordingly for this sort of thing.

If you use Digital Ocean, signing up with our referral link via the button below would be appreciated!  You will get $100 credit as a new customer, and we'll get a referral credit after your first paid invoice.

<a href="https://www.digitalocean.com/?refcode=17eecba47b58&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge"><img src="https://web-platforms.sfo2.cdn.digitaloceanspaces.com/WWW/Badge%201.svg" alt="DigitalOcean Referral Badge" /></a>

### License

AGPL, because you are free to use this code as you see fit to publish your own content. Or even provide custom code based on this to others for a fee, if you are a developer and wish to work as a media hosting consultancy, for example, provided that you also release the source code you have added or changed. What you're not free to do is use this repository's original code as a basis for a closed-source "service"... like Patreon or Substack.  The point of all this is to have less of them, not enable more of them.

### Contributing

PRs are welcome! Please discuss new features you would like to see in the [discussions](https://github.com/RentFreeMedia/rentfreemedia/discussions) area so that we can keep the issues forum prioritized for bug reports. The [Needs / Wants](https://github.com/RentFreeMedia/rentfreemedia/issues/2) thread atop the issues forum is an up-to-date list of priorities for the future.

As Wagtail is a CMS that sits on top of, in front of, Django... feature proposals should integrate with Wagtail. While it's possible to do anything in code, doing it with future maintainability in mind is also a big consideration. Would-be contributors and custom solution developers would be wise to not only thoroughly read the [Wagtail docs](https://docs.wagtail.org), but also read the Wagtail code itself. 

The code should work with the Django development server, with some caveats:

* Premium media will not 'play' directly without Nginx to respond to the X-Sendfile request. You'll see 200 response codes for them in the console / logs after they successfully authenticate, though.
* There are some complex queries in the premium media RSS feeds that only work with PostgreSQL. As of this writing SQLite and MySQL do not support `distinct('field_name')` and thus will not work with this distribution in production. There is an error check against the payment app `views.py` that will allow SQLite to work in dev mode, but you must use Postgres in production and the "subscribe" page in dev mode may have duplicate entries on SQLite.
* The code should run fine on Linux and Mac (as well as any other BSD Unix) but I don't test against Windows, so let us know if you have any Windows issues / solutions.

### Local Development

To run the project locally:

1. Download and unzip the repo or a release. The "main" branch should always be stable, the "dev" branch should be the most recent.
2. Edit `env` in the root of the rentfree directory and provide the required settings, then save the edited file as `.env`. Remote storage options are not required for development mode, it will serve the media files and static files from your local machine. At minimum, specify email server info, stripe account sandbox public/private key and webhook secret, the base_url of 127.0.0.1, and the human readable site name.
3. Make a virtual environment (`python3 -m venv ~/rentfreelibs`)
4. Activate the virtual environment (`~/rentfreelibs/bin/activate`)
5. Edit `manage.py` and set the settings target to "dev" instead of "prod"
6. Edit `website/wsgi.py` and set the settings target to "dev" instead of "prod"
7. `pip install -r requirements.txt`
8. `pip install django-debug-toolbar`
9. `python3 manage.py makemigrations && python3 manage.py migrate`
10. `python3 manage.py createsuperuser`
11. `python3 manage.py runserver`

You should now be up and running on http://127.0.0.1:8000
