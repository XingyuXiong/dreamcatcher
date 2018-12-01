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
from uuid import uuid4
import datetime

import requests

from .cas_client_v2 import CASClientV2
from .single_logout_mixin import SingleLogoutMixin

SAML_1_0_NS = 'urn:oasis:names:tc:SAML:1.0:'
SAML_1_0_PROTOCOL_NS = '{' + SAML_1_0_NS + 'protocol' + '}'
SAML_1_0_ASSERTION_NS = '{' + SAML_1_0_NS + 'assertion' + '}'
SAML_ASSERTION_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<SOAP-ENV:Body>
<samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
MajorVersion="1"
MinorVersion="1"
RequestID="{request_id}"
IssueInstant="{timestamp}">
<samlp:AssertionArtifact>{ticket}</samlp:AssertionArtifact></samlp:Request>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

class CASClientWithSAMLV1(CASClientV2, SingleLogoutMixin):
    """CASClient 3.0+ with SAML"""

    def verify_ticket(self, ticket, **kwargs):
        """Verifies CAS 3.0+ XML-based authentication ticket and returns extended attributes.

        @date: 2011-11-30
        @author: Carlos Gonzalez Vila <carlewis@gmail.com>

        Returns username and attributes on success and None,None on failure.
        """

        page = self.fetch_saml_validation(ticket)

        try:
            user = None
            attributes = {}
            response = page.content
            tree = ElementTree.fromstring(response)
            # Find the authentication status
            success = tree.find('.//' + SAML_1_0_PROTOCOL_NS + 'StatusCode')
            if success is not None and success.attrib['Value'].endswith(':Success'):
                # User is validated
                name_identifier = tree.find('.//' + SAML_1_0_ASSERTION_NS + 'NameIdentifier')
                if name_identifier is not None:
                    user = name_identifier.text
                attrs = tree.findall('.//' + SAML_1_0_ASSERTION_NS + 'Attribute')
                for at in attrs:
                    if self.username_attribute in list(at.attrib.values()):
                        user = at.find(SAML_1_0_ASSERTION_NS + 'AttributeValue').text
                        attributes['uid'] = user

                    values = at.findall(SAML_1_0_ASSERTION_NS + 'AttributeValue')
                    if len(values) > 1:
                        values_array = []
                        for v in values:
                            values_array.append(v.text)
                            attributes[at.attrib['AttributeName']] = values_array
                    else:
                        attributes[at.attrib['AttributeName']] = values[0].text
            return user, attributes, None
        finally:
            page.close()

    def fetch_saml_validation(self, ticket):
        # We do the SAML validation
        headers = {
            'soapaction': 'http://www.oasis-open.org/committees/security',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'accept': 'text/xml',
            'connection': 'keep-alive',
            'content-type': 'text/xml; charset=utf-8',
        }
        params = {'TARGET': self.service_url}
        saml_validate_url = urllib_parse.urljoin(
            self.server_url, 'samlValidate',
        )
        return requests.post(
            saml_validate_url,
            self.get_saml_assertion(ticket),
            params=params,
            headers=headers)

    @classmethod
    def get_saml_assertion(cls, ticket):
        """
        http://www.jasig.org/cas/protocol#samlvalidate-cas-3.0

        SAML request values:

        RequestID [REQUIRED]:
            unique identifier for the request
        IssueInstant [REQUIRED]:
            timestamp of the request
        samlp:AssertionArtifact [REQUIRED]:
            the valid CAS Service Ticket obtained as a response parameter at login.
        """
        # RequestID [REQUIRED] - unique identifier for the request
        request_id = uuid4()

        # e.g. 2014-06-02T09:21:03.071189
        timestamp = datetime.datetime.now().isoformat()

        return SAML_ASSERTION_TEMPLATE.format(
            request_id=request_id,
            timestamp=timestamp,
            ticket=ticket,
        ).encode('utf8')