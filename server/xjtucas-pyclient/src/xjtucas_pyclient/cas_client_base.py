#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

from six.moves.urllib import parse as urllib_parse

import requests

from .cas_error import CASError

class CASClientBase(object):

    logout_redirect_param_name = 'service'

    def __init__(self, service_url=None, server_url='https://cas.xjtu.edu.cn',
                 extra_login_params=None, renew=False,
                 username_attribute=None):

        self.service_url = service_url
        self.server_url = server_url
        self.extra_login_params = extra_login_params or {}
        self.renew = renew
        self.username_attribute = username_attribute
        pass

    def verify_ticket(self, ticket):
        """must return a triple"""
        raise NotImplementedError()

    def get_login_url(self):
        """Generates CAS login URL"""
        params = {'service': self.service_url}
        if self.renew:
            params.update({'renew': 'true'})

        params.update(self.extra_login_params)
        url = urllib_parse.urljoin(self.server_url, 'login')
        query = urllib_parse.urlencode(params)
        return url + '?' + query

    def get_logout_url(self, redirect_url=None):
        """Generates CAS logout URL"""
        url = urllib_parse.urljoin(self.server_url, 'logout')
        if redirect_url:
            params = {self.logout_redirect_param_name: redirect_url}
            url += '?' + urllib_parse.urlencode(params)
        return url

    def get_proxy_url(self, pgt):
        """Returns proxy url, given the proxy granting ticket"""
        params = urllib_parse.urlencode({'pgt': pgt, 'targetService': self.service_url})
        return "%s/proxy?%s" % (self.server_url, params)

    def get_proxy_ticket(self, pgt):
        """Returns proxy ticket given the proxy granting ticket"""
        response = requests.get(self.get_proxy_url(pgt))

        try:
            from lxml import etree
        except ImportError:
            import xml.etree.ElementTree as etree

        if response.status_code == 200:
            root = etree.fromstring(response.content)
            tickets = root.xpath(
                "//cas:proxyTicket",
                namespaces={"cas": "http://www.yale.edu/tp/cas"}
            )
            if len(tickets) == 1:
                return tickets[0].text
            errors = root.xpath(
                "//cas:authenticationFailure",
                namespaces={"cas": "http://www.yale.edu/tp/cas"}
            )
            if len(errors) == 1:
                raise CASError(errors[0].attrib['code'], errors[0].text)
        raise CASError("Bad http code %s" % response.status_code)
