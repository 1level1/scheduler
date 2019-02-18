from rest_framework import serializers
from django.contrib.auth.models import User

from scheduler.models import Day, Department, Role, Schedule, DutyLimit, DayLimit, DepartmentInternRoleList


class DayLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayLimit
        fields = ('id','date','limit','intern','department')

class DutyLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyLimit
        fields = '__all__' # all model fields will be included


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('role_id','role','roleRestrictions')

        
class DaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Day
        fields = ('day_id', 'type', 'interns')

        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('department_id','name','rolesList','InternsList','schedules')


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('schedule_id','days')
        
class InternSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')

class DepartmentInternRoleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentInternRoleList
        fields = ('id','department_id','user','role_id')
        
