# Publishing Indexes

Publishing index pages, whether it be a podcst or written articles or even video, is very similar to the process of creating the home page you went through in the previous section.  The only difference will be the data you put in the pages.

## Adding Child Pages

Head back to the `pages` menu in the main left hand admin menu once you return to the CMS admin, and click the `home` page folder icon.

The large green menu atop the page browser always lets you `edit` your current page position in the index, so you could edit the home page again from here, and also `add a child page` underneath it in the larger middle section of the page if you want to make a new child of your present position in the page tree.

Note that certain pages can only be added at certain positions in the page tree.  This is by design, to ensure that pages which inherit data from their parent pages are always in the proper place.  For example, you can only create a `Podcast Content Page` (i.e. an episode) underneath an `Index Page for a Podcast`.  If you're looking to create a particular type of content and can't find it in your `add a child page` options, you're probably in the wrong place in the page tree and need to navigate a step higher or lower to get to the proper location.  `Generic Page` is a freeform content type that can be added anywhere in the tree.

Lets create an `Index Page for a Podcast` and its associated RSS feed.  From the `Home` section of the page tree browser, click `add a child page` and select `Index Page for a Podcast` as the content type.

## Creating a Podcast Feed

By default, the `Index Page for a Podcast` and `Index Page for Articles` page types don't need any content added to the main body of the page, but you are welcome to add more if you wish via the main editor tab.  Absent any other options, they will display a paginated list of all of the articles, blog posts, or episodes published beneath the index page.  They also automatically create RSS feeds that can be published to podcast directories or used in feed readers to read articles via RSS, including authenticated ones for paying subscribers which we will get into later in this guide.

First, head to the `layout` tab in the editor and you'll see some options that you can change.  `Show child pages` will be selected by default, this causes the index page to display a list of its children as an index. You can change the number of episodes or articles per page if you like from the default of 10, by changing the number in `number per page` to a different value. `Order child pages by` can be changed as well, but for our podcast example we can leave the default of `publish date, newest first` alone. 

Lastly for the `layout` section, you can enable or disable the display of episode images, headlines (`captions`), author information, and date information on the index page.  These settings only affect the display on your site, not on external podcast directories or feed readers, so you can choose whichever options you prefer.

## Setting up the RSS feed

The `SEO` tab of the `Index Page for a Podcast` page editor contains the bulk of the settings you'll be concerned with when publishing a podcast via this framework.  Let's go through them all one by one.

* `slug` again, is the permanent URL of the page.  Could be as simple as "episodes" or as complex as "my-awesome-podcast." This will be a part of your feed URL, though, so choose wisely.  If your primary purpose for using this framework is publishing a podcast, and you want your URLs to look like [mypodcast.com/episodes](https://mypodcast.com/episodes) then keeping it simple here is probably what you want.
* `title tag` and `meta description` are what will display on places like Google, Twitter, and Facebook when this page is linked on those sites, so you can change these options here.
* `open graph preview image` is the image that will show on places like Google, Twitter, and Facebook, so you can click the button and upload an image for that purpose here if you like.

## Main RSS Feed Settings

Next we have the main RSS feed settings that are specific to a podcast, so lets specify what our test podcast feed will look like.

* `main entity of site` concerns JSON+LD schema.org metadata, which the site generates for search indexes automatically.  Select "yes" here if this podcast will be the main content type that your site will publish, otherwise select "no."
* `rss title`, and `rss TTL` should be familiar to you if you have published a podcast before, these are your RSS feed's main title, logo / cover image, and time between episodes that you want indexes to wait before checking for a new one.
* `rss image` and `rss premium image` should also be familiar if you have seen a premium-tier podcast before. The first image setting will set the main public feed's image, and the premium image will set the cover logo for the paid subscriber feed.

At this point it's worth noting that the tooltips below each form field are written to be as helpful and descriptive as possible.  For instance, if you notice the tooltip below `TTL` says that you can specify this value in "hours:minutes" format or plain "minutes" format.  For instance, there are 1440 minutes in a day so putting 1440 in the `TTL` field will set that value in the feed.  If you were to input "23:59" instead, it the editor will automatically convert the value to "1439" for you when the page is saved.

You will also notice that some fields in the editor have a red `*` next to them and some do not.  The red `*` denotes a required field that must be filled in, while fields without the red dot are optional and may be left blank if you don't want to fill them in.

Moving along in our new podcast feed...

* `rss description` is the main description of your show in this case. HTML is enabled, and the buttons are limited to HTML tags that Apple/iTunes support. Moving your mouse over each one will show you what clicking one of the HTML tag buttons will create.
* `rss_category` and `rss_subcategory` options are precisely what they appear to be, allowing you to select a main (and optional sub) category twice for Apple's podcast directory. 
* `iTunes explicit` sets whether or not your show has explicit language
* `iTunes type` controls whether or not your show will have season designators, or be listed as a a plain series of episodes.  If you select `serial` here, your site index page for podcasts will also paginate the episodes by season as well.
* `combine feeds` controls whether or not the public episodes and the private episodes a paying user subscribe to will appear combined in their personal subscription feed or not.
* `episode numbers` controls whether or not episode numbers are shown in the RSS feed
* `preview prefix` will prepend episodes marked as preview of subscriber content with a string, if you publish previews of paid episodes in the public feed. For example "PREVIEW - "
* `omit previews` will select whether or not preview episodes exist in the public RSS feed. If no, you'll still publish public preview pages for paid episodes on the site, but they will be skipped over as the RSS feed is generated.

The optional fields may be filled in or not depending on your preference. Their tooltips explain their behavior.

There is no `preview` for index pages since there isn't any content beneath them to show you immemdiately after you create them, so you can go ahead and click the `lower arrow` and directly `publish` the podcast index page once you're happy with all of the options you've chosen.

## Important Concepts in This Section


1. `Add a child page` is limited based on your position in the page tree menu, to automatically handle the simplest of errors, such as trying to put a podcast episode outside of its index for example. If you can't find the content type you want when creating a page, check your position in the page tree, it's probably slightly off and you just need to navigate to the right place.
2. The content for `Index Page for a Podcast` and `Index Page for Articles` pages is controlled almost entirely in the `layout` tab, you don't need to manually specify any content in the main body of the page, unless you want to provide some extra functionality.
3. The `SEO` tab of the index page types contains all of the podcast RSS feed options you need to specify when publishing a podcast or video cast.
4. The `SEO` tab also contains the metadata fields that let you customize the appearance of pages on Google and social media sites when linked on those services.
5. There's no `preview` when creating an index page type, because there isn't content beneath it to show you immediately after the index's creation, so the `preview` button will not show a page preview if you try to use it on an index page.

Next, we will publish an episode in our new podcast index.