from django.test import TestCase
from django.http import HttpRequest

from secretballot.middleware import (SecretBallotMiddleware,
                                     SecretBallotIpMiddleware,
                                     SecretBallotIpUseragentMiddleware)
from .models import Link


class MiddlewareTestCase(TestCase):
    def test_ip_middleware(self):
        mw = SecretBallotIpMiddleware()
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        mw.process_request(r)
        assert r.secretballot_token == '1.2.3.4'

    def test_ip_ua_middleware(self):
        mw = SecretBallotIpUseragentMiddleware()

        # basic token
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        mw.process_request(r)
        ff_token = r.secretballot_token

        # same one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Firefox'
        mw.process_request(r)
        ff_token2 = r.secretballot_token

        assert ff_token == ff_token2

        # different one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = 'Chrome'
        mw.process_request(r)
        chrome_token = r.secretballot_token

        assert ff_token != chrome_token

        # blank one
        r = HttpRequest()
        r.META['REMOTE_ADDR'] = '1.2.3.4'
        r.META['HTTP_USER_AGENT'] = ''
        mw.process_request(r)
        blank_token = r.secretballot_token

        assert ff_token != blank_token

    def test_no_token(self):
        mw = SecretBallotMiddleware()
        with self.assertRaises(NotImplementedError):
            mw.process_request(HttpRequest())


class TestBasicVoting(TestCase):

    def test_basic_voting(self):
        l = Link.objects.create(url='https://google.com')
        assert Link.objects.get().vote_total == 0

        l.add_vote('1.2.3.4', 1)
        assert Link.objects.get().vote_total == 1

        l.add_vote('1.2.3.5', 1)
        assert Link.objects.get().vote_total == 2

        l.add_vote('1.2.3.6', -1)
        assert Link.objects.get().vote_total == 1
