#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

__VERSION__ = '0.2'

from .cas_client_v1 import CASClientV1
from .cas_client_v2 import CASClientV2
from .cas_client_v3 import CASClientV3
from .cas_client_with_saml_v1 import CASClientWithSAMLV1

class CASClient(object):
    def __new__(self, *args, **kwargs):
        version = kwargs.pop('version')
        if version in (1, '1'):
            return CASClientV1(*args, **kwargs)
        elif version in (2, '2'):
            return CASClientV2(*args, **kwargs)
        elif version in (3, '3'):
            return CASClientV3(*args, **kwargs)
        elif version == 'CAS_2_SAML_1_0':
            return CASClientWithSAMLV1(*args, **kwargs)
        raise ValueError('Unsupported CAS_VERSION %r' % version)

    @staticmethod
    def getVersion():
        return __VERSION__
