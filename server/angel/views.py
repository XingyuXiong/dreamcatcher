from django.views.generic import View
from django.views.decorators.http import require_POST, require_GET
from common import ok, error, extract, ExtractException, optional_extract
from xjtucas_pyclient import Client as CASClient, InvalidCASTicketException
from .models import Angel, Group, Honor
from .avatar import unify as unify_avatar, AvatarException


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
                'logged_in':
                True,
                'angel':
                Angel.objects.get(id=request.session['angel_id']).to_dict()
            })
        else:
            back_url = self._build_url(request, back_path)
            client = CASClient(back_url)
            return ok({'logged_in': False, 'redirect': client.get_login_url()})

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
def update_angel(request):
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
        try:
            angel.avatar = unify_avatar(avatar)
        except AvatarException as ex:
            return ex.response
    angel.save()

    return ok(angel.to_dict())


@require_GET
def get_angel(request):
    try:
        id_list = extract(request, 'id_list')
    except ExtractException as ex:
        return ex.response

    return ok([
        angel.to_dict()
        for angel in Angel.objects.filter(id__in=id_list).all()
    ])


@require_POST
def logout_angel(request):
    del request.session['angel_id']
    return ok()


@require_GET
def get_group(request):
    try:
        id_list = extract(request, 'id_list')
    except ExtractException as ex:
        return ex.response

    return ok([
        group.to_dict()
        for group in Group.objects.filter(id__in=id_list).all()
    ])


@require_POST
def update_group(request, group_id):
    try:
        name, description, deleted_angels, avatar = optional_extract(
            request, ['name', 'description', 'deleted_angels'],
            file_key='avatar')
    except ExtractException as ex:
        return ex.response

    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return error('invalid group ID')

    if request.angel.led_group != group:
        return error('angel does not own this group')

    if name is not None:
        group.name = name
    if description is not None:
        group.description = description
    if deleted_angels is not None:
        # print(deleted_angels)
        if request.angel.id in deleted_angels:
            return error('cannot delete leader from group')
        for angel in group.angels.filter(id__in=deleted_angels):
            angel.group = None
            angel.save()
    if avatar is not None:
        try:
            group.avatar = unify_avatar(avatar)
        except AvatarException as ex:
            return ex.response
    group.save()

    return ok(group.to_dict())


@require_GET
def get_honor(request):
    try:
        id_list = extract(request, 'id_list')
    except ExtractException as ex:
        return ex.response

    return ok([
        honor.to_dict()
        for honor in Honor.objects.filter(id__in=id_list).all()
    ])
