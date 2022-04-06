# Publishing Content

Content pages are where your actual episodes, articles, or videos will live, beneath the indexes like the one we created in the previous section. In this portion of this tutorial we will create a podcast episode as an example.

## Creating an Episode

After you publish the `Index Page for a Podcast` that we set up in the previous section of this tutorial, you will have that page appear in the page tree beneath the home page. Just as you did before, navigate to the podcast index page in the page tree menu, and click the folder icon.

As mentioned in the previous step, certain content types are restricted by location in the page tree.  This is another example of that concept, as `Podcast Episode Pages` can only be created underneath an `Index Page for a Podcast`.  In fact the *only* page content type you can create beneath an `Index Page for a Podcast` is a podcast episode, so click on `add child page` while viewing your previously created `Index Page for a Podcast` and you will immediately be taken to the podcast episode page creation form.

## Primary Episode Data

Immediately atop the Podcast Episode Page form, you will be presented with required fields which must be filled in. The `title` is the same as the title on other pages, and will give the page editor words to create the automatically generated `slug` in the `SEO` tab as well, which you can optionally change if you like.

The `cover image` controls what image will be shown alongside the episode on this website. If the `SEO` tab og metadata fields are left blank the `cover image` will also become the Google search / social media preview metadata image on those other sites and services as well.  This field is optional, if you omit the image no image will be shown on this website's index listings, but it doesn't affect the episode's appearance in RSS feed(s).

The `episode number` is exactly what it suggests, specify `1` here for now since this is the first episode we'll publish in this index.

`Episode type` is an optional field, do not specify it unless the episode you're publishing meets the criteria in the dropdown list. This only affects the episode's display in the public RSS feed, by flagging it as a bonus or trailer if you choose one of those options.

`Preview?` works hand-in-hand with the preview prefix setting we declared on the index page we created previously.  If the episode is flagged as a preview of a paid episode here, and there is a prefix setting in the index, the preview prefix you defined will be applied to this episode's title in the show's RSS feed. If this is not a preview episode and / or you do not want to prefix preview episodes in your public RSS feed, select `no` here.  For this episode choose `no` and we'll publish a public episode as an example.

`Front Page?` works with template variables on the site to control whether or not this episode appears in page preview lists in other pages on the site. For example, perhaps we might add a "latest episodes" list to our home page after we have created a few episodes of a podcast, and we might also want to omit certain episodes from that list. You can selectively omit episodes from that list by changing this `front page` setting to `no` but for now lets leave the default of `yes` as this will be a public / free episode.

`Caption` is a headline field.  It represents what should be a short, one sentence description of this episode or article you are creating. `Caption` is appended to the beginning of the article body or episode notes in the RSS feed when it is generated.  So let's put something simple here, like "This is my first episode."

`Publish date` is exactly what it describes. If you need to manually set the publish date it can be changed by clicking on the field and specifying something other than today, but the current date and time is chosen by default when you create the page in the editor.  Note that the editor has an option to publish content at a specified date in the future from a draft in the page editor's `settings` tab, but this is not that setting, this is only the `publish date` used for display and sorting purposes.

## Authors and Contributors

This section introduces a new concept in Wagtail called a "clusterable" object. In short what this means is that you can add more than one item to a single field, which obviously applies to Hosts (Authors) and Contributors (Guests).  This same functionality exists in identical form on Article pages.

You specify your hosts by selecting `author/host/creator` and choosing a user account from the list.  The name that will appear on the live site goes through a series of conditional what-ifs, the most prominent of which is the "name" box you can specify here in the editor.  If you want to customize how a person's name appears specify it here.

If the person specified has a `first_name` and `last_name` in their user profile it will next display those if no name is specified in the page content editor.  Next, if they have only a `first_name` in their profile it will display their `first_name` only.  Lastly, if they have no first name or last name and no name specified in the page editor, but they have a `user_name` in their profile, it will display their user name.  There is also a URL setting on user accounts that may be specified by admins but isn't shown to users.  If you wish to allow a guest to link their user profile to some thing they are promoting, for example, you can specify that URL on their user account in `settings` and `users` from the main CMS left hand menu and the URL will be the clickable link associated with their name and profile picture on the show notes page.

Contributors perform in an identical way as authors/hosts, the only difference being that the user accounts you can choose as a contributor are limited to those who belong to a contributor group.

There is no special permission attached to the contributor group, by default it simply exists for this purpose of limiting the choices for guest contributors selectable in content pages. You can add users to it by going to `settings`, `groups` in the main left hand CMS menu, and then selecting the contributor group and clicking `view users in this group` in the green menu atop the form, after which there will be a button that allows you to `add a user` to the group. After adding a user to the contributor group their email address will be selectable as a contributor in content page creation forms.

Multiple Authors/Hosts and Contributors/Guests can be specified on a podcast or article page. After filling out the form for one, simply click the respective `author/host/creator` or `contributor` button again to add another.

## Adding Media

Next, you specify what type and the location of media files that will be associated with this episode of your podcast or video cast.  You may either upload a media file that you host directly, or link one that is hosted remotely. There is an error check here that will only allow you to choose one or the other, only one audio or video file per page is supported under the podcast page content type.

When specifying remote media content types, you can also link youtube and vimeo videos, which will be embedded in the custom player interface on your site.

The image selectors on the remote and local media fields will place a thumbnail image in your RSS feed which will be displayed on podcast directories as an image specific to this episode. Whether to add one or not is your choice.  If you omit these images, the episode image field will be blank in the RSS feed and your main show image will be used as a default.

For considerations about media upload file sizes, see the Managing Media section of this guide.

## Extra Settings Tabs

Once all of the secondary data of your podcast episode is specified, it's a good time to take a look at the other page / content options in the other tabs in the editor.

* `tags` are keyword tags that serve two purposes. One, they will create categories on your site that allow users to click on a tag and get other episodes with similar content in them. Secondly, tags are embedded in your LD+JSON schema.org markup to specify keywords attached to the content in question for search engines, as well.  Tags autocomplete to encourage you to re-use common tags over and over. Simply start typing in the tag form, and if you have used a tag with a similar spelling before it should appear as an option that you can select.  The `tab` key on your keyboard completes a tag and starts a new one.  You can specify as many or as few tags as you like.
* the `layout` tab allows you to specify a header and footer menu that will appear on the page, which may be defined as `snippets` in the main CMS left hand menu. Snippets are sections of content that are not specific to a page which may be re-used on multiple pages.
* the `SEO` tab has open graph metadata options like you had in the `Index Page for a Podcast` page you created earlier, and they perform the same functions here. You can override the image, title, and description that will appear on social media links to this episode by specifying them here, and you can also customize the permanent URL of the episode by changing the `slug` if you wish.
* the `settings` tab has some useful features for asynchronus publishing and marketing purposes. First, you may schedule an episode to be posted at a future date (and then saving it as a draft). Secondly, you may optionally have an episode *un-published* which could be useful for temporary "unlocks" of premium content, for example. You may also define a paywall in the `settings` tab, which will show a user a pop-up modal alerting them to whatever information you wish to show them. Content walls, like headers and footers, are defined as `snippets` which we will go through in detail. later in this tutorial.

## The Episode Notes / Body

The episode notes that will appear in your RSS feed and on podcast directories that parse the feed are comprised of two things: 1, the main body text, and 2 the `caption` or 'headline' from your site. 

At this point we have arrived at a new concept, the `streamfield` portion of the page.  This is a feature specific to Wagtail, the CMS backend of Rent Free Media.  It allows you to place what will appear on your published page, in the order you want them to appear in, and control the basic layout dynamically within the page editor in the CMS admin, all without writing any code.

While you have control over the order and visibility of streamfield blocks in your finished page, the blocks will still be rendered with the templates specified in HTML/CSS code, resulting in a consistent look, feel, and user experience throughout your site.

In the simplest of terms, if you include a block in the streamfield editor, it will be shown on the page.  If you omit the block, it will not be shown.  If you change the order of the blocks, the order in which they appear on the page will also be changed respectively.

For a podcast episode page, the only required streamfield block is the body text, which when combined with the `caption` will become the episode notes that appear in your RSS feed and on podcast directories. 

Lets create a podcast episode page body in the streamfield with all of the data we've specified to this point displayed.

Step 1. Click `title and heading data` in the streamfield page body editor, and the block will appear at the top of your page body items list. This block has no data to specify, it takes its information from the episode title and caption that you've already specified above.

Step 2. Click the `+` beneath title and heading data to add another block, and then click `authors and contributors` in the streamfield editor, and the block will appear below the title and heading data block. This block also does not have any data to specify, it takes its information from the authors and contributors you provided above.

Step 3. Click the `+` beneath authors and contributors, and select `emebed local media`. This block provides a player embedded in the page for video and audio files. Like the previous two, this block has no information for you to specify, it will embed a player for whichever type of media you chose to attach to this page in the previous steps.

Step 4. Click the `+` beneath embed local media, and select `main body text`. Here you must choose which format you wish to write your episode notes in.  Rich Text is a WYSIWYG type rich text editor similar to a Google Docs file, and Markdown is... well... Markdown.  If you like Markdown you already know what it is.

Write some random text in whichever format you prefer for the main body text.

Step 5. Click the `+` beneath main body text, and select `user comments` in the streamfield block menu. This will add a block that renders the user comment section beneath the main body text. Again, there's no data to specify here, including the block in the list simply chooses whether or not comments will appear on the page.

At this point your episode page is complete. You can click `preview` next to the page save action menu at the bottom of the editor and you should see all of the page rendered as a user would see it on the live site, with all of the data filled in. As mentioned before in this guide, you can change any data you like, in any of the settings tabs in the editor, and click `preview` again to verify that the result is what you want.

When you're satisfied with all of the data and changes you've made, click `publish` in the menu above save draft to publish the page live.

## Seeing Your RSS Feed

As soon as you've published the above episode live, it will appear in the public RSS feed for your podcast. You can pull up the feed by going to the URL slug you specified on your episode index page, and appending `/rss/` to the end of the address.

For instance, if your episode index page was named and slugged "Episodes" your podcast RSS feed will be available at [http://127.0.0.1:8000/episodes/rss/](http://127.0.0.1:8000/episodes/rss/) for the purposes of this tutorial, or https://mysite.com/episodes/rss/ in the case of a live website.

Note that Chrome and Firefox will show you the raw output of an RSS feed (or optionally download it so that you can view it in a text editor) but Safari will not.

## Publishing Written Articles

If you are publishing written articles instead of podcast episodes, all of the above information is still applicable.  All of the features of a written article page are present in a podcast page, with podcast-specific items omitted.  A written article index will also generate an RSS feed available at the same address as if you had created a podcast index and feed, so that your users may read your articles in a feed reader app or device.

## Important Concepts in This Section


1. There are settings in `podcast content pages` which interact with the index, and must be defined at the beginning of the new episode page form. You should read the tooltips and this guide to understand how these work together.
2. `Caption` and `Main Body Text` are also related, in that they will be merged together when your episode is submitted to podcast indexers.  `Caption` is also the one-sentence headline on your site, so you should write the two with this relation in mind.
3. `Tags` not only categorize your content for users of your site, but also get submitted to search engines as keywords.
4. `Header` and `Footer` snippets can be defined per-page to add head and foot menus to each page.
5. `Scheduled publishing` can be used to schedule episodes to post at a future date, as well as schedule "unlock promo" episodes to be un-published at a future date, by defining options in the page editor `settings` tab. To employ this feature, simply choose the dates and times you wish to trigger and save the episode as a draft, the rest will be handled automatically.
6. `Content walls` (paywalls) can be added to pages selectively in the page editor `settings` tab, and are also defined as `snippets` like headers and footers.
7. The `streamfield` is what you use to define what will actually appear on your page's main body. You can display data or not, block by block, while keeping all of the data required to build your RSS feed present.

Next, we will build some `snippets`, also with `streamfield` blocks, to define a header and footer which can be used throughout the site.