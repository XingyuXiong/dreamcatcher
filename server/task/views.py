from django.views.generic import View
from django.views.decorators.http import require_POST, require_GET
from django.utils.timezone import now
from common import ok, get_object_with_id_list, extract, ExtractException, \
    error
from .models import Task, TaskStatus


class TaskView(View):
    def get(self, request):
        return get_object_with_id_list(request, Task)

    def post(self, request):
        try:
            description = extract(request, 'description')
            payment = extract(request, 'payment')
        except ExtractException as ex:
            return ex.response
        task = Task(description=description, cost=payment, owner=request.angel)
        task.save()
        return ok(task.to_dict())


@require_GET
def get_available_task(request):
    pushed_task_set = request.session['pushed_task_set'] or set()
    task_id_list = list(
        Task.objects.exclude(
            id__in=pushed_task_set).order_by('cost')[:20].values_list(
                'id', flat=True))
    request.session['pushed_task_set'] |= set(task_id_list)
    return ok(task_id_list)


@require_GET
def get_related_task(request):
    try:
        finished = extract(request, 'finished')
    except ExtractException:
        finished = None

    owned = request.angel.owned_tasks
    helped = request.angel.helped_tasks
    if finished is True:
        owned = owned.exclude(
            status__in=[TaskStatus.FINSIHED.value, TaskStatus.CANCELED.value])
        helped = helped.exclude(
            status__in=[TaskStatus.FINSIHED.value, TaskStatus.CANCELED.value])

    return ok(
        list(owned.values_list('id', flat=True)) +
        list(helped.values_list('id', flat=True)))


@require_POST
def accept_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return error('invalide task ID')

    if task.owner == request.angel:
        return error('cannot accept owned task')

    if task.status != TaskStatus.CREATED.value:
        return error('task is not acceptable')

    task.helper = request.angel
    task.status = TaskStatus.ACCEPTED.value
    task.accepted_at = now()
    task.save()

    return ok(task.to_dict())


@require_POST
def finish_task(request, task_id):
    try:
        contribution = extract(request, 'contribution')
    except ExtractException as ex:
        return ex.response

    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return error('invalid task ID')

    if task.status != TaskStatus.COMPLETED:
        return error('task is not completed')

    if task.helper != request.angel:
        return error('cannot finish not-helped task')

    if contribution < 0 or contribution > task.cost:
        return error('invalid contribution value')

    task.contribution = contribution
    task.helper.contribution += contribution
    # TODO: what about returned money?
    task.status = TaskStatus.FINSIHED.value
    task.finished_at = now()
    task.save()
    task.helper.save()

    return ok(task.to_dict())


@require_POST
def complete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return error('invalide task ID')

    if task.status != TaskStatus.ACCEPTED:
        return error('task is not accepted')

    if task.owner != request.angel:
        return error('cannot complete not-owned task')

    task.status = TaskStatus.COMPLETED.value
    task.completed_at = now()
    task.save()

    return ok(task.to_dict())


@require_POST
def cancel_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return error('invalide task ID')

    if task.status in [TaskStatus.FINSIHED.value, TaskStatus.COMPLETED.value]:
        return error('cannot cancel completed task')

    if task.owner != request.angel:
        return error('cannot cancel not-owned task')

    task.status = TaskStatus.CANCELED
    task.canceled_at = now()
    task.save()

    return ok(task.to_dict())
