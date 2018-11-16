from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

import json

from .models import Angel
from .angel_fetcher import AngelFetcher
from .middleware import with_angel


@require_GET
@ensure_csrf_cookie
def info(request):
    if 'angel_id' in request.session:
        angel = Angel.objects.get(pk=request.session['angel_id'])
        return JsonResponse({
            'success': True,
            'message': 'ok',
            'data': {
                'login_required': False,
                'angel': {
                    'id': angel.id,
                    'nickname': angel.nickname,
                }
            },
        })
    else:
        return JsonResponse({
            'success': True,
            'message': 'ok',
            'data': {
                'login_required': True,
            }
        })


class LoginRequestHandler(AngelFetcher):
    def on_exist_angel(self, angel, request):
        request.session['angel_id'] = angel.id
        return JsonResponse({
            'success': True,
            'message': 'ok',
            'data': {
                'ticket_required': False,
                'exist': True,
                'angel': {
                    'id': angel.id,
                    'nickname': angel.nickname,
                }
            },
        })

    def on_create_angel(self, reg_name, reg_id, netid, request):
        angel = Angel(
            registered_name=reg_name,
            registered_id=reg_id,
            identifier=netid,
            nickname=reg_name,
            score=0,
        )
        angel.save()
        request.session['angel_id'] = angel.id
        return JsonResponse({
            'success': True,
            'message': 'ok',
            'data': {
                'ticket_required': False,
                'exist': False,
                'angel': {
                    'id': angel.id,
                    'nickname': angel.nickname,
                    'registered_id': angel.registered_id,
                    'registered_name': angel.registered_name,
                }
            },
        })


@require_POST
def login(request):
    return LoginRequestHandler().fetch(request)


@require_POST
@with_angel
def logout(request):
    del request.session['angel_id']
    return JsonResponse({
        'success': True,
        'message': 'ok',
    })


@require_POST
@with_angel
def update(request):
    angel = request.angel
    for key, value in request.POST.items():
        if key == 'nickname':
            angel.nickname = value
        else:
            return JsonResponse({
                'success': False,
                'message': 'unexpect update key'
            })
    angel.save()
    return JsonResponse({
        'success': True,
        'message': 'ok',
    })
