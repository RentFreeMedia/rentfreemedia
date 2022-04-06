from djstripe import webhooks
from django.db import transaction

""" this file is an example of how you might configure custom events triggered by stripe data."""

def do_something():
    pass  # change pass to some other function, to send a mail, invalidate a cache, fire off a task, etc.

@webhooks.handler('plan', 'product', 'customer', 'subscription')
def my_handler(event, **kwargs): # pass the event data object and associated keys/values
    if event.type == 'product': # check what type of event it is
        transaction.on_commit(do_something) # after the database commits stripe product data, do a thing
    else: # else, if the event type check doesn't match 'product'
        pass # do nothing

""" all of this is optional, the core site functionality knows if a subscriber is 'active' (paid) and 
    knows if events received from stripe are valid. however, if you need some functionality not present
    in the data synchronization between your database and stripe's database, this is the way to do it."""