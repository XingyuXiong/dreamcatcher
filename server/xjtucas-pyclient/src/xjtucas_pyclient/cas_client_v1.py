#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Package: xjtucas_pyclient
Author: xczh <zhuxingchi@tiaozhan.com>

Copyright (C) 2016 tiaozhan. All Rights Reserved.
"""

from six.moves.urllib import parse as urllib_parse

import requests

from .cas_client_base import CASClientBase

class CASClientV1(CASClientBase):
    """CAS Client Version 1"""

    logout_redirect_param_name = 'url'

    def verify_ticket(self, ticket):
        """Verifies CAS 1.0 authentication ticket.

        Returns username on success and None on failure.
        """
        params = [('ticket', ticket), ('service', self.service_url)]
        url = (urllib_parse.urljoin(self.server_url, 'validate') + '?' +
               urllib_parse.urlencode(params))
        page = requests.get(url, stream=True)
        try:
            page_iterator = page.iter_lines(chunk_size=8192)
            verified = next(page_iterator).strip().decode()
            print('verified: ', verified)
            if verified == 'yes':
                return next(page_iterator).strip().decode(), None, None
            else:
                return None, None, None
        finally:
            page.close()