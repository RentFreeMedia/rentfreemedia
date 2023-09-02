# Deploy Live

If you've made it this far you're ready to deploy your site live to the world and start building your audience.

We provide Ansible scripts for deployment of all of the code in this project to Digital Ocean, who make the most sense in terms of bandwidth pricing and features to host this.  Among the cloud services Digital Ocean has:

1. $0.01 per gigabyte outgoing bandwidth pricing, which is roughly 1/8 to 1/10 the price of Azure, AWS, and Google Cloud by comparison
2. An S3-compatible storage service with CDN that "just works" with our included storage backend for images, static files, and media files.
3. A well mantained API to automate the deployment process which is rather complex to handle manually.

## Installing Dependencies

To run the provided deployment scripts, you need a few optional dependencies.

To install them, run:

`ansible-galaxy collection install amazon.aws community.crypto community.digitalocean community.general `

## Setting your SSH private key

In the file `ansible/main.yml` there's a variable at the top which specifies which private key you wish to use on the server(s) after deployment.

My example is in there as the default:

`ansible_ssh_private_key_file:` /Users/robertclayton/.ssh/rentfree_rsa

You should change /Users/xxx/.ssh/rentfree.rsa to your own private SSH key.

## Running

Next, execute the following to start the deployment:

`ansible-playbook ./main.yml -i "mydomain.com",` where mydomain.com is your root domain name.

You'll need to be logged into your Digital Ocean dashboard when you start the script, as it will ask you for things like API keys, S3 access keys, etc.  You'll also need your email server authentication information and SMTP server information if you are not using a common email service like gmail or yahoo or similar.

The scripts will set up a complete installation of Rent Free Media on Digital Ocean in its own project namespace, including DNS records.

Note that for SSL key issuance to work, you'll need to have pointed your domain name's DNS servers to Digital Ocean beforehand.

## Post Setup

When the script has finished and you confirm that your site is alive, you're not quite done yet.  You will surely need to set up your mail server information in your DNS records according to your mail service's instructions, so be sure to do that lest your user notification emails wind up in the spam folders of your users.

If you are using an API based email service as recommended, you'll need to change the default email backend in `website / settings / prod.py` in the `POST_OFFICE` section to:

`anymail.backends.(your_supported_mail_service).EmailBackend`

...and configure Anymail as explained in their docs, here:

[https://anymail.dev/en/stable/esps/](https://anymail.dev/en/stable/esps/)

You'll also need to verify via your Stripe dashboard that webhook events are being sent successfully to your web server.

After doing the above you'll probably want to send a test email to yourself via the `Send Email` menu in the CMS admin to ensure outgoing mail is working.

If it doesn't all work right away, give it an hour or so and try again, as it may take a while for DNS changes to spread out.

When your site responds to its domain name, and you can successfully log into your CMS admin section, and the Stripe webhook events are being successfully sent, you're in business. All you have left to do is build your site and publish your content.

Enjoy!
