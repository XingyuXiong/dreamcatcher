#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

from .cas_client_v2 import CASClientV2
from .single_logout_mixin import SingleLogoutMixin

class CASClientV3(CASClientV2, SingleLogoutMixin):
    """CAS Client Version 3"""
    url_suffix = 'serviceValidate'
    logout_redirect_param_name = 'service'

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
                attributes[tag] = attribute.text
        return attributes

    @classmethod
    def verify_response(cls, response):
        return cls.parse_response_xml(response)