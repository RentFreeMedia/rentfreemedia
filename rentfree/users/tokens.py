from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, time
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

class UnsubscribeTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return str(user.email) + str(user.is_mailsubscribed) + str(login_timestamp) + str(timestamp)

unsubscribe_token = UnsubscribeTokenGenerator()


class SubscribeTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        paysubscribe_timestamp = '' if user.paysubscribe_changed is None else user.paysubscribe_changed.replace(microsecond=0, tzinfo=None)
        return str(user.email) + str(user.is_paysubscribed) + str(user.uuid) + str(paysubscribe_timestamp) + str(timestamp)

subscribe_token = SubscribeTokenGenerator()

class CardChangeTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        paysubscribe_timestamp = '' if user.paysubscribe_changed is None else user.paysubscribe_changed.replace(microsecond=0, tzinfo=None)
        return str(user.email) + str(user.is_paysubscribed) + str(user.uuid) + str(paysubscribe_timestamp)

cardchange_token = CardChangeTokenGenerator()

class PremiumSubscriberTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return str(user.id) + str(user.download_resets) + str(user.is_paysubscribed) + str(user.uuid) + str(user.stripe_subscription.status)

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
            # RemovedInDjango40Warning.
            legacy_token = len(ts_b36) < 4
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            # RemovedInDjango40Warning: when the deprecation ends, replace
            # with:
            #   return False
            if not constant_time_compare(
                self._make_token_with_timestamp(user, ts, legacy=True),
                token,
            ):
                return False

        # RemovedInDjango40Warning: convert days to seconds and round to
        # midnight (server time) for pre-Django 3.1 tokens.
        now = self._now()
        if legacy_token:
            ts *= 24 * 60 * 60
            ts += int((now - datetime.combine(now.date(), time.min)).total_seconds())
        # Check the timestamp is within limit.
        if (self._num_seconds(now) - ts) > 3153600000:
            return False

        return True

premium_token = PremiumSubscriberTokenGenerator()
