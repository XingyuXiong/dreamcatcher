from django.urls import reverse
from common import error
from .models import Angel


def login_required_middleware(get_response):
    exclude_path_list = [
        reverse('angel:login'),
    ]

    def middleware(request):
        if request.path in exclude_path_list:
            return get_response(request)
        if 'angel_id' not in request.session:
            return error('not logged in')
        angel_id = request.session['angel_id']

        try:
            request.angel = Angel.objects.get(id=angel_id)
        except Angel.DoesNotExist:
            return error(f'angel (id={angel_id}) does not exist')

        return get_response(request)

    return middleware
