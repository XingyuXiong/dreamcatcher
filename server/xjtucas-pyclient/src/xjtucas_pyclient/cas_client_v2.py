#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

from six.moves.urllib import parse as urllib_parse
try:
    from xml.etree import ElementTree
except ImportError:
    from elementtree import ElementTree

import requests

from .cas_client_base import CASClientBase

class CASClientV2(CASClientBase):
    """CAS Client Version 2"""

    url_suffix = 'serviceValidate'
    logout_redirect_param_name = 'url'

    def __init__(self, proxy_callback=None, *args, **kwargs):
        """proxy_callback is for V2 and V3 so V3 is subclass of V2"""
        self.proxy_callback = proxy_callback
        super(CASClientV2, self).__init__(*args, **kwargs)

    def verify_ticket(self, ticket):
        """Verifies CAS 2.0+/3.0+ XML-based authentication ticket and returns extended attributes"""
        response = self.get_verification_response(ticket)
        return self.verify_response(response)

    def get_verification_response(self, ticket):
        params = {
            'ticket': ticket,
            'service': self.service_url
        }
        if self.proxy_callback:
            params.update({'pgtUrl': self.proxy_callback})
        base_url = urllib_parse.urljoin(self.server_url, self.url_suffix)
        page = requests.get(base_url, params=params)
        try:
            return page.content
        finally:
            page.close()

    @classmethod
    def parse_attributes_xml_element(cls, element):
        attributes = dict()
        for attribute in element:
            tag = attribute.tag.split("}").pop()
            if tag in attributes:
                if isinstance(attributes[tag], list):
                    attributes[tag].append(attribute.text)
                else:
                    attributes[tag] = [attributes[tag]]
                    attributes[tag].append(attribute.text)
            else:
                if tag == 'attraStyle':
                    pass
                else:
                    attributes[tag] = attribute.text
        return attributes

    @classmethod
    def verify_response(cls, response):
        user, attributes, pgtiou = cls.parse_response_xml(response)
        if len(attributes) == 0:
            attributes = None
        return user, attributes, pgtiou

    @classmethod
    def parse_response_xml(cls, response):
        user = None
        attributes = {}
        pgtiou = None

        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            for element in tree[0]:
                if element.tag.endswith('user'):
                    user = element.text
                elif element.tag.endswith('proxyGrantingTicket'):
                    pgtiou = element.text
                elif element.tag.endswith('attributes'):
                    attributes = cls.parse_attributes_xml_element(element)
        return user, attributes, pgtiou