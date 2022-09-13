from itertools import chain
import datetime
from django.db.models import Q
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from timetracker.services import format_response, get_current_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from .models import *
from .serializers import *
from .services import *


class ProjectList(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        self.user_id = get_current_user(request)
        self.user = User.objects.get(pk=self.user_id)

    def get_object(self, pk):
        try:
            project = Project.objects.get(pk=pk, user=self.user)
            return project
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk:
            project = self.get_object(pk)
            return Response(format_response(ProjectDataSerializer(project).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            projects = self.user.my_projects.all()
            results = self.paginate_queryset(projects, request, view=self)
            return Response(
                format_response(ProjectDataSerializer(results, many=True).data, 'Success', 200, projects.count()),
                status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(user=self.user)

            # Add into Member
            Member.objects.create(user=self.user, project=project, role=1)

            return Response(format_response(ProjectDataSerializer(project).data, 'Success', 201),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            return Response(format_response(ProjectDataSerializer(project).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        project = self.get_object(pk)
        project.delete()
        return Response(format_response([], 'Deleted', 204), status=status.HTTP_204_NO_CONTENT)


class ProjectTimeLog(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        self.user_id = get_current_user(request)
        self.user = User.objects.get(pk=self.user_id)

    def get_object(self, pk):
        try:
            project = Project.objects.get(pk=pk, members__user__in=[self.user])
            return project
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk:
            # Get project
            project = self.get_object(pk)

            # Get member
            member = request.GET.get('member', self.user_id)
            if member is None:
                return Response(format_response({'member': ['Member User ID is required']}, 'Bad Request', 400),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check member exists
            members = [obj.user_id for obj in project.members.all()]
            if int(member) not in members:
                return Response(format_response({'user': ['User not found in this project']}, 'Bad Request', 400),
                                status=status.HTTP_400_BAD_REQUEST)

            # Get and prepare date
            date = request.GET.get('date', None)
            if date is None:
                date = datetime.date.today()
            else:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')

            start_date = datetime.datetime.combine(date, datetime.datetime.min.time())
            end_date = datetime.datetime.combine(date, datetime.datetime.max.time())

            # Timelog
            timelog = TimeLog.objects.filter(member__user_id=member, start__range=[start_date, end_date])

            return Response(format_response(TimeLogDataSerializer(timelog, many=True).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            return Response(format_response([], 'Success', 200), status=status.HTTP_200_OK)


class MemberList(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        self.user_id = get_current_user(request)
        self.user = User.objects.get(pk=self.user_id)

    def get_object(self, pk):
        try:
            # If current user is Admin
            return Member.objects.get(pk=pk, project__user=self.user)
        except Member.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk:
            member = self.get_object(pk)
            return Response(format_response(MemberDataSerializer(member).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            return Response(format_response([], 'Success', 200), status=status.HTTP_200_OK)

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            # Check ownership
            is_owner = check_ownership(self.user, request.data.get('project'))
            if is_owner is False:
                return Response(format_response({'project': ['You are not owner of this project']}, 'Bad Request', 400),
                                status=status.HTTP_400_BAD_REQUEST)

            # Check duplicate
            project = serializer.validated_data.get('project')
            members = list(project.members.values_list('user_id', flat=True))
            if int(request.data.get('user')) in members:
                return Response(format_response({'user': ['User already exists']}, 'Bad Request', 400),
                                status=status.HTTP_400_BAD_REQUEST)

            # Save Member
            member = serializer.save()
            return Response(format_response(MemberDataSerializer(member).data, 'Success', 201),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # Get member
        member = self.get_object(pk)

        # Copy payload and update user
        data = request.data.copy()
        data['user'] = member.user_id

        serializer = MemberSerializer(member, data=data)
        if serializer.is_valid():
            member = serializer.save()
            return Response(format_response(MemberDataSerializer(member).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_object(pk)
        member.delete()
        return Response(format_response([], 'Deleted', 204), status=status.HTTP_204_NO_CONTENT)


class TimeLogList(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        self.user_id = get_current_user(request)
        self.user = User.objects.get(pk=self.user_id)

    def get_object(self, pk):
        try:
            # If Admin or current user
            return TimeLog.objects.get((Q(member__user=self.user) | Q(member__project__user=self.user)), pk=pk)
        except TimeLog.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        if pk:
            timelog = self.get_object(pk)
            return Response(format_response(TimeLogDataSerializer(timelog).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            # Get all my membership
            membership = self.user.my_membership.all()

            # Merge all timelog project wise
            timelogs = []
            for member in membership:
                timelog = member.time_log.all()
                timelogs = list(chain(timelogs, timelog))

            return Response(format_response(TimeLogDataSerializer(timelogs, many=True).data, 'Success', 200),
                            status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TimeLogSerializer(data=request.data)
        if serializer.is_valid():
            # Check permission
            has_permission = check_member_permission(self.user, serializer.validated_data.get('member'))
            if has_permission is False:
                return Response(format_response({'project': ['You are not allowed to add timelog']}, 'Bad Request', 400),
                                status=status.HTTP_400_BAD_REQUEST)

            # Save Timelog
            timelog = serializer.save()
            return Response(format_response(TimeLogDataSerializer(timelog).data, 'Success', 201),
                            status=status.HTTP_201_CREATED)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        # get timelog
        timelog = self.get_object(pk)

        # Copy payload and update member
        data = request.data.copy()
        data['member'] = timelog.member_id

        serializer = TimeLogSerializer(timelog, data=data)
        if serializer.is_valid():
            timelog = serializer.save()
            return Response(format_response(TimeLogDataSerializer(timelog).data, 'Success', 200),
                            status=status.HTTP_200_OK)
        else:
            return Response(format_response(serializer.errors, 'Bad Request', 400), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        timelog = self.get_object(pk)
        timelog.delete()
        return Response(format_response([], 'Deleted', 204), status=status.HTTP_204_NO_CONTENT)
