from django.http import JsonResponse
from django.views import View
from angel.middleware import with_angel

from datetime import datetime

from .models import Task


@with_angel
def show_general_info(request):
    angel = request.angel
    try:
        owned_task = angel.owned_task.exclude(is_finished=True).get()
    except Task.DoesNotExist:
        owned_task = None
    accepted_tasks = angel.accepted_tasks.exclude(is_finished=True).all()
    other_tasks = Task.objects\
        .exclude(id__in=[
            task.id for task in accepted_tasks
        ] + ([owned_task.id] if owned_task is not None else [])) \
        .exclude(is_finished=True) \
        .all()
    return JsonResponse({
        'success': True,
        'message': 'ok',
        'data': {
            'owned': owned_task.id if owned_task is not None else None,
            'accepted': [task.id for task in accepted_tasks],
            'available': [task.id for task in other_tasks],
        },
    })


@with_angel
def compute_point(request):
    cost = request.GET.get('cost', None)
    if cost is None:
        return JsonResponse({
            'success': False,
            'message': 'cost is not provided',
        })
    point = request.angel.calculate_point(cost)
    return JsonResponse({
        'success': True,
        'message': 'ok',
        'data': {
            'point': point,
        }
    })


@with_angel
def submit_task(request):
    desc = request.POST.get('description', None)
    cost = request.POST.get('cost', None)
    if desc is None or cost is None:
        return JsonResponse({
            'success': False,
            'message': 'desc or cost is not provided',
        })

    point = request.angel.calculate_point(cost)
    task = Task(description=desc, cost=cost, point=point,
                owner=request.angel, helper=None)
    task.save()

    return JsonResponse({
        'success': True,
        'message': 'ok',
        'data': {
            'id': task.id,
        }
    })


class TaskView(View):
    def get(self, request):
        return show_general_info(request)

    def post(self, request):
        return submit_task(request)


def get_task_info(request, taskID):
    task = Task.objects.get(pk=taskID)
    return JsonResponse({
        'success': True,
        'message': 'ok',
        'data': {
            'id': task.id,
            'description': task.description,
            'point': task.point,
            'owner_id': task.owner.id,
            'helper_id': task.helper.id if task.helper is not None else None,
            'is_finished': task.is_finished,
        },
    })


@with_angel
def accept_task(request, taskID):
    task = Task.objects.get(pk=taskID)
    task.helper = request.angel
    task.save()
    return JsonResponse({
        'success': True,
        'message': 'ok'
    })

@with_angel
def finish_task(request, taskID):
    task = Task.objects.get(pk=taskID)
    if task.owner != request.angel:
        return JsonResponse({
            'success': False,
            'message': 'angel does not own this task',
        })
    helper = task.helper
    if helper is None:
        return JsonResponse({
            'success': False,
            'message': 'no helper exists'
        })
    task.is_finished = True
    task.finished_time = datetime.now()
    task.save()
    helper.score += task.point
    helper.save()
    return JsonResponse({
        'success': True,
        'message': 'ok',
    })
