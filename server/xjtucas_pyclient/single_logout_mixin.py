#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

from lxml import etree

class SingleLogoutMixin(object):
    @classmethod
    def get_saml_slos(cls, logout_request):
        """returns saml logout ticket info"""
        try:
            root = etree.fromstring(logout_request)
            return root.xpath(
                "//samlp:SessionIndex",
                namespaces={'samlp': "urn:oasis:names:tc:SAML:2.0:protocol"})
        except etree.XMLSyntaxError:
            pass