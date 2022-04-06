# Forms

Rent Free Media contains two custom form options, which have varying degrees of complexity.  In both cases, the form submissions are stored as dynamic data in the admin that can be exported as a CSV (spreadsheet).  If you need forms that store data in pre-set database tables, you would need to follow the Django form methods which are well documented in the Django docs.  Rent Free Media forms are meant to be dynamic and createable in the CMS admin.

You can create a form page anywhere under the "Home" page of your site, and also embed a form in any other page as a "page preview block" in a streamfield if you want a more complex page layout with a form embedded in it.

## Success Page

Before creating forms, you should create a "success" page of type "generic page" somewhere below your home page, to direct users to after they have submitted the form.  You probably also would want a button on that page (or perhaps a button in your footer for said page) that gives the user the option to return "home" or to another page.

## Basic Forms

The basic form type has simple fields that you can specify in the CMS admin upon creation.  Submissions will show up in a `Forms` menu in the CMS admin that appears when there are form submissions to display.

To create fields for your form, simply add multiple fields specifying the options for each, in the same manner that you would add multiple authors or contributors to a content page.

You may also define confirmation emails that are sent upon successful form submission at the bottom of the `Basic Form` editor if you so choose.  The fields are just like the fields used to create an email in the `Send Email` portion of this guide.

## Complex Forms

Rent Free Media also supports "dynamic" forms, which is to say... forms that change conditionally based on user input and have multiple pages of form steps.

To create a complex form choose that type when creating a form, and start by defining a form "step" each of which will be a "page" in the form process.

The editor for a complex form is a streamfield like the page editor, you add form fields that you wish the user to fill in just like you would add streamfield blocks to a page.

The complex part of a complex form becomes apparent when you open the "settings" button of a form step.  Here, you can specify a field to be conditionally shown or hidden based on a prior form input.

For example, let's create a form with three text fields.

* Label: Sky (default value: "blue")
* Label: Grass (default value: "green")
* Label: Correct (default value: "good job!")

Give your form page a name at the top of the editor, and choose a success page.

Next, click the settings button on "grass" and give the field a CSS ID of `grass`

Then, click the settings button on the "correct" field, and give the field a `condition trigger ID` of "grass" and a `condition trigger value` of "green" and then preview the form.

You'll see all three fields rendered because the default values are "correct" but change the grass field to anything except green, and press tab as if you were a user filling out the form.  You'll notice that the "correct" box disappeared because the value of "grass" is no longer "green" which you specified as a condition for the field's existence.

Using this logic you can build many complex multi-step forms to collect conditional user data.

## Embedding a Form

As mentioned above, you aren't limited to putting forms on pages alone without other content.  To embed a form in another page, publish a form page and then edit the streamfield of another page, and select the "page preview" block where you want the form to appear, and select the form page as the source for the page preview block.

By this method, you can embed forms in other pages throughout the site rather than having them stand alone as pages of their own.

