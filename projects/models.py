from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_projects')
    title = models.CharField('Title', max_length=255)
    description = models.TextField('Description', blank=True, null=True)
    STATUS = (
        (0, 'InActive'),
        (1, 'Active'),
    )
    status = models.SmallIntegerField('Status', choices=STATUS, default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Member(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_membership')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    ROLE = (
        (1, 'Admin'),
        (2, 'Member')
    )
    role = models.SmallIntegerField('Role', choices=ROLE, default=2)
    STATUS = (
        (1, 'Pending'),
        (2, 'Approved'),
        (3, 'Inactive')
    )
    status = models.SmallIntegerField('Status', choices=STATUS, default=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project.title


class TimeLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='time_log')
    memo = models.TextField('Memo', null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    TYPE = (
        (1, 'Software Tracked'),
        (2, 'Manual Entry')
    )
    type = models.SmallIntegerField('Type', choices=TYPE, default=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.member.user.first_name
