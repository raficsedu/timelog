from rest_framework import serializers
from users.serializers import UserDataSerializer
from .models import *


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['user', 'project', 'role', 'status']


class MemberDataSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    role = serializers.SerializerMethodField()

    def get_role(self, member):
        return member.get_role_display()

    class Meta:
        model = Member
        fields = ['id', 'user', 'project', 'role', 'status', 'created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status']


class ProjectDataSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    def get_members(self, project):
        return MemberDataSerializer(project.members.all(), many=True).data

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'status', 'created_at', 'updated_at', 'members']


class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ['member', 'memo', 'start', 'end']


class TimeLogDataSerializer(serializers.ModelSerializer):
    member = MemberDataSerializer()

    class Meta:
        model = TimeLog
        fields = ['id', 'member', 'memo', 'start', 'end', 'type', 'created_at', 'updated_at']
