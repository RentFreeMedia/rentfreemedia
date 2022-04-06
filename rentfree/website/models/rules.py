from django.db.models import ForeignKey, SET_NULL
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel
from wagtail_personalisation.rules import AbstractBaseRule

class TierEqualOrGreater(AbstractBaseRule):
    """User is logged in, subscribed to a product tier,
    currently paid up, and the subscription tier is
    greater than or equal to the level specified.
    """
    icon = 'user'

    tier_level = ForeignKey('djstripe.Product', verbose_name=_('Tier greater or equal to:'), null=True, on_delete=SET_NULL)

    panels = [
        FieldPanel('tier_level'),
    ]

    class Meta:
        verbose_name = _('Tier Greater or Equal rule')

    def test_user(self, request=None):
        if request.user.is_anonymous:
            user = None
        else:
            user = request.user

        if user and self.tier_level:
            if user.is_paysubscribed >= int(self.tier_level.metadata['tier']):
                if user.stripe_subscription.status == 'active':
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def description(self):

        return {
            'title': _('User is paid subscriber at or above this tier:'),
            'value': 'Tier ' + self.tier_level.metadata['tier'],
            'code': True
        }


class TierEqual(AbstractBaseRule):
    """User is logged in, subscribed to a product tier,
    currently paid up, and the subscription tier is
    equal (only) to the level specified.
    """
    icon = 'user'

    tier_level = ForeignKey('djstripe.Product', verbose_name=_('Tier equal to:'), null=True, on_delete=SET_NULL)

    panels = [
        FieldPanel('tier_level'),
    ]

    class Meta:
        verbose_name = _('Tier Equal Rule')

    def test_user(self, request=None):
        if request.user.is_anonymous:
            user = None
        else:
            user = request.user

        if user and self.tier_level:
            if user.is_paysubscribed == int(self.tier_level.metadata['tier']):
                if user.stripe_subscription.status == 'active':
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def description(self):

        return {
            'title': _('User is paid subscriber equal to this tier:'),
            'value': 'Tier ' + self.tier_level.metadata['tier'],
            'code': True
        }