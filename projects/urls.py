from django.urls import path
from . import views

urlpatterns = [
    # Project
    path('list', views.ProjectList.as_view(), name='project'),
    path('list/<int:pk>', views.ProjectList.as_view(), name='project_by_id'),
    path('list/timelog/<int:pk>', views.ProjectTimeLog.as_view(), name='project_timelog'),

    # Member
    path('member/list', views.MemberList.as_view(), name='member'),
    path('member/list/<int:pk>', views.MemberList.as_view(), name='member_by_id'),

    # Timelog
    path('timelog/list', views.TimeLogList.as_view(), name='timelog'),
    path('timelog/list/<int:pk>', views.TimeLogList.as_view(), name='timelog_by_id'),
]
