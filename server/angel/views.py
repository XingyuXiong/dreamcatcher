from django.views.generic import View
from django.views.decorators.http import require_POST
from common import ok, error, extract, ExtractException, optional_extract
from xjtucas_pyclient import Client as CASClient, InvalidCASTicketException
from .models import Angel, Group


class LoginView(View):
    def _build_url(self, request, path):
        return f'{request.scheme}://{request.get_host()}{path}'

    def get(self, request):
        try:
            back_path = extract(request, 'back')
        except ExtractException as ex:
            return ex.response

        if 'angel_id' in request.session:
            return ok({
                'logged_in': True,
                'angel': Angel.objects.get(
                    id=request.session['angel_id']).to_dict()
            })
        else:
            back_url = self._build_url(request, back_path)
            client = CASClient(back_url)
            return ok({
                'logged_in': False,
                'redirect': client.get_login_url()
            })

    def post(self, request):
        try:
            back_path = extract(request, 'back')
            ticket = extract(request, 'ticket')
        except ExtractException as ex:
            return ex.response

        back_url = self._build_url(request, back_path)
        client = CASClient(back_url)
        try:
            xjtu_net_id, registered_name, registered_id = \
                client.verify_ticket(ticket)
        except InvalidCASTicketException:
            return error('invalid login ticket')

        identifier = 'XJTU-' + xjtu_net_id
        try:
            angel = Angel.objects.get(identifier=identifier)
        except Angel.DoesNotExist:
            angel = Angel(
                registered_name=registered_name,
                registered_id=registered_id,
                identifier=identifier,
                nickname=registered_name,
            )
            angel.save()
        return ok(angel.to_dict())


@require_POST
def update(request):
    try:
        nickname, phone, group_id, avatar = optional_extract(
            request, ['nickname', 'phone', 'group_id'], file_key='avatar')
    except ExtractException as e:
        return e.response

    angel = request.angel
    if nickname is not None:
        angel.nickname = nickname
    if phone is not None:
        angel.phone = phone
    if group_id is not None:
        try:
            angel.group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return error(f'group (id={group_id}) does not exist')
    if avatar is not None:
        #
        angel.avatar = avatar
    angel.save()

    return ok(angel.to_dict())
