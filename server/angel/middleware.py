from django.http import QueryDict, JsonResponse
from django.utils.decorators import decorator_from_middleware

import json

from .models import Angel


# https://gist.github.com/LucasRoesler/700d281d528ecb7895c0
class JSONMiddleware:
    """
    Process application/json requests data from GET and POST requests.
    """

    def process_request(self, request):
        def json_to_query_set(data):
            # for consistency sake, we want to return
            # a Django QueryDict and not a plain Dict.
            # The primary difference is that the QueryDict stores
            # every value in a list and is, by default, immutable.
            # The primary issue is making sure that list values are
            # properly inserted into the QueryDict.  If we simply
            # do a q_data.update(data), any list values will be wrapped
            # in another list. By iterating through the list and updating
            # for each value, we get the expected result of a single list.
            q_data = QueryDict('', mutable=True)
            for key, value in data.items():
                if isinstance(value, list):
                    # need to iterate through the list and upate
                    # so that the list does not get wrapped in an
                    # additional list.
                    for x in value:
                        q_data.update({key: x})
                else:
                    q_data.update({key: value})
            return q_data

        if request.method == 'POST' and 'CONTENT_TYPE' in request.META and \
                'application/json' in request.META['CONTENT_TYPE']:
            # load the json data
            data = json.loads(request.body)
            request.POST = json_to_query_set(data)
        if request.method == 'GET' and 'data' in request.GET:
            data = json.loads(request.GET['data'])
            request.GET = json_to_query_set(data)

        return None

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self._get_response(request)


class AngelMiddleware:
    def process_request(self, request):
        if 'angel_id' in request.session:
            request.angel = Angel.objects.get(pk=request.session['angel_id'])
            return None
        else:
            return JsonResponse({
                'success': False,
                'message': 'not log in',
            })


with_angel = decorator_from_middleware(AngelMiddleware)
