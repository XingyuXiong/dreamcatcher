from django.http import JsonResponse
from urllib.parse import unquote, quote

import json

import sys
import os
old_path = list(sys.path)
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), 'xjtucas-pyclient', 'src'))
from xjtucas_pyclient import CASClient
sys.path = old_path

from .models import Angel


class AngelFetcher:
    def on_exist_angel(self, angel):
        raise NotImplementedError

    def on_create_angel(self, registered_name, registered_id, identifier):
        raise NotImplementedError

    def fetch(self, request):
        if 'back' not in request.POST:
            return JsonResponse({
                'success': False,
                'message': 'back URL is not provided',
            })
        back_url = request.POST['back']

        cas_client = CASClient(version='CAS_2_SAML_1_0', service_url=back_url)
        if 'ticket' not in request.POST:
            return JsonResponse({
                'success': True,
                'message': 'please redirect to CAS login page',
                'data': {
                    'ticket_required': True,
                    'redirect_url': cas_client.get_login_url(),
                },
            })
        ticket = request.POST['ticket']

        try:
            netid, attr, _pgt = cas_client.verify_ticket(ticket)
        except Exception:
            netid = None
        if netid is None:
            return JsonResponse({
                'success': False,
                'message': 'invalid CAS ticket',
            })

        try:
            angel = Angel.objects.get(identifier=netid)
        except Angel.DoesNotExist:
            reg_name = unquote(attr['cn'])
            reg_id = attr['employeeNumber']
            return self.on_create_angel(reg_name, reg_id, netid, request)

        return self.on_exist_angel(angel, request)
