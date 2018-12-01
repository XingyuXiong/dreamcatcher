#
from django.http import JsonResponse
import json


def ok(data=None):
    resp = {
        'success': True,
        'message': 'ok',
    }
    if data is not None:
        resp['data'] = data
    return JsonResponse(resp)


def error(message):
    return JsonResponse({
        'success': False,
        'message': message,
    })


class ExtractException(Exception):
    def __init__(self, message):
        self.response = error(message)


def _get_query_set(request):
    if request.method == 'GET':
        if 'data' not in request.GET:
            raise ExtractException(f'missing request arguments')
        query_set = json.loads(request.GET['data'])
    elif request.method == 'POST':
        query_set = request.POST
    else:
        raise Exception()
    return query_set


def extract(request, name):
    query_set = _get_query_set(request)
    if name not in query_set:
        raise ExtractException(f'missing "{name}" argument')
    return query_set[name]


def optional_extract(request, param_keys, file_key=None):
    query_set = _get_query_set(request)
    result = []
    for key in param_keys:
        result.append(query_set.get(key, None))
    if file_key is not None:
        result.append(
            request.FILES[file_key] if file_key in request.FILES else None)
    if all([value is None for value in result]):
        file_desc = [f"<file: {file_key}>"] if file_key is not None else []
        raise ExtractException(
            f'at least one of {param_keys + file_desc} should be passed')
    return tuple(result)
