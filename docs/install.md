# Installing

Installation for local development or test usage is similar to other Django / Wagtail projects, with a few small caveats. You'll need a Python v3 installation, which should be included if you're doing this on a Linux machine, or you can download a Mac version of Python from [python.org](https://python.org). 

Once you have a version of Python 3 installed, go through the following steps, executing the bolded commands in a terminal window. Commands and actions you perform are in `red`.

## Initial Setup

Step 1. Download the latest release from the main repository, or clone/fork the development branch if you plan to make changes to the underlying code.  If you unzip it to your home folder you should be able to move to that folder (replace with wherever you unzipped or cloned the repo to):

`cd ~/rentfree`

Step 2. Make a virtual environment

`python3 -m venv ~/rentfreelibs`

Step 3. Activate it

`~/rentfreelibs/bin/activate`

Step 4. Install the required dependencies

`pip install -r requirements.txt`

Step 5. Make migrations and migrate

`python3 manage.py makemigrations`

`python3 manage.py migrate`

Step 6. Create an admin user

`python3 manage.py createsuperuser`

Step 7. Start the local test server

`python3 manage.py runserver`

At this point the test site should be up and running at [http://127.0.0.1:8000/](http://127.0.0.1:8000).  You should check that in your browser to make sure it's working.  It will say "Welcome to your new Wagtail site" (or something similar if that message changes since this was written).

Let's first get rid of the default page and specify the site settings.

## A New Home Page

Once the test server is running, head to [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) and login with the admin email and password that you provided in the above step.  

Then, lets make a page to replace the "welcome to Wagtail" default page.  Click on `pages` in the left hand grey menu, then click on the `home` icon at the very top of the pop-out menu.  You should arrive at a page titled `Root`.

From here, `add a child page` and give it a random title (we'll come back and change it in a minute), and then `save draft`.

After you've saved the new page, go to `settings` all the way at the bottom of the left hand main admin menu, and click on `sites` in the pop-out menu.  From here, change the port to `8000` since that is the port your test server is running on, and change the hostname to `127.0.0.1` since that is is the address where the test server is running.

Lastly, choose the new page you just created as the home page for the site, and then `save`.

At this point you can navigate back to `pages` at the top of the left hand main admin menu, go back to the root pages section via the house icon at the top, and `delete` the "Welcome to Wagtail" default home page.  You do so by moving your mouse over the page, and selecting `delete` from the `more` menu.

Once you've deleted the default home page, you can `edit` the page you created a minute ago into your new home page.  Change the title of the page to "Home" (capitalization will be respected here), under the `SEO` tab atop the page editor change the `slug` of the page to "home" (this is the URL of pages other than the default home page), and under the `Layout` tab of the page editor, select "home page without title and cover image" as the `template`.

After doing all of this click the `preview` button next to "save draft" and a new window should open in your browser with a preview of the page you're about to publish.  It's always a good idea to preview before publishing for obvious reasons: as pages get more complex you need to check for errors before pages "go live."  After the preview shows you the spiffy blank white page you have created, click the `lower arrow` next to "save draft" and select `publish`. 

Congratulations, at this point you have published your first page.  You can click `view live` in the green menu if you like to show the live page, and it should be blank rather than saying "Welcome to your new Wagtail site."  Your browser back button after viewing the live page should bring you back to the admin section.

## Important Concepts in This Section


1. `Save draft` makes a page that is only visible to other editors and admins. A page isn't public until you `publish` it.  Feel free to use this collaboratively, that's what it's there for.  Multiple people can work on a draft, and only `publish` when they're sure it's all ready to go.
2. The `slug` under the `SEO` tab is the page's permanent URL.  By default the CMS will choose one for you based on the first page title you type in the title field, but it's a good idea to double check, and you can always change it if you like, with the caveat that since slugs are URLs they must be unique.
3. The `settings` portion of the main admin menu contains global settings for the entire site. Feel free to go through the other menus and fill in things that make obvious sense. For instance there are social media URL fields, a Google Analytics API field if you use Google Analytics, a schema.org SEO metadata section, etc.  Don't worry if some don't make sense or can't be selected yet, we'll cover them all over the course of this tutorial.
4. It's always a good idea to `preview` before publishing a page to check for mistakes. Preview will always reload your most recent changes to the page editor, even if the page hasn't been saved yet.  Preview will also alert you to any errors in the page editor forms, such as required fields that you have neglected to fill in, for example.

Now head to the Publishing Indexes section of this guide, and lets make a podcast.
