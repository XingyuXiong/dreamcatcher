from django.db import models
from django.conf import settings
import hashlib


# https://stackoverflow.com/a/31733919
def _hashed_name(inst, _filename):
    inst.avatar.open()
    content = inst.avatar.read(inst.avatar.DEFAULT_CHUNK_SIZE)
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest() + '.jpg'


class Angel(models.Model):
    registered_name = models.CharField(max_length=30)
    registered_id = models.CharField(max_length=30)
    identifier = models.CharField(max_length=100, unique=True)
    nickname = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    avatar = models.ImageField(upload_to=_hashed_name)
    group = models.ForeignKey(
        'Group', null=True, on_delete=models.SET_NULL, related_name='angels')
    contribution = models.FloatField(default=0.0)
    honors = models.ManyToManyField('Honor')

    def to_dict(self, has_group=True):
        result = {
            'id': self.id,
            'registered_id': self.registered_id,
            'registered_name': self.registered_name,
            'nickname': self.nickname,
            'avatar':
                self.avatar.url if bool(self.avatar)
                else settings.STATIC_URL + 'angel_avatar_default.jpg',
            'contribution': self.contribution,
            'honors': list(self.honors.values_list('id', flat=True)),
        }
        if has_group:
            result['group'] = self.group.to_dict(no_members=True) \
                if self.group is not None else None
        return result


class Group(models.Model):
    name = models.CharField(max_length=30)
    avatar = models.ImageField(upload_to=_hashed_name)
    description = models.TextField()
    leader = models.OneToOneField(
        Angel, on_delete=models.PROTECT, related_name="led_group")
    honors = models.ManyToManyField('Honor')

    def to_dict(self, no_members=False):
        result = {
            'id': self.id,
            'name': self.name,
            'avatar':
                self.avatar.url if bool(self.avatar)
                else settings.STATIC_URL + 'group_avatar_default.jpg',
            'description': self.description,
            'leader': self.leader.to_dict(has_group=False),
            'honors': list(self.honors.values_list('id', flat=True)),
        }
        if not no_members:
            result['angels'] = [
                member.to_dict(has_group=False) for member in self.angels.all()
            ]
        return result


class Honor(models.Model):
    description = models.TextField()
    logo = models.ImageField()
