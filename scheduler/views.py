from rest_framework.parsers import JSONParser
from scheduler.models import *
from scheduler.serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from rest_framework import status
from django.db.models.query import QuerySet
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from ScheduleEngine.DutySchedule import *
from ScheduleEngine.ShceduleCalendar import *
from django.contrib.auth import authenticate, login, logout
import json
import ScheduleEngine

# Create your views here.
####################################
#
#    Intern
#
####################################

class InternsList(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        interns = User.objects.all()
        serializer = InternSerializer(interns, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        
        user_token = request.data.get('token')
        if not user_token:
              return Response("No sign in token was provided",status=402)
        user = authenticate(request,token=user_token)
        if user is not None:
            login(request, user)
            serializer = InternSerializer(user)
            return Response(serializer.data, status=201)
        raise Http404
#         intern_obj=Intern.objects.filter(email=request.data['email'])
#         if len(intern_obj)==1:
#             serializer = InternSerializer(intern_obj[0])
#             return Response(serializer.data)
#         serializer = InternSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 validate_email(request.data['email'])
#             except ValidationError:
#                 return Response("Not a legal email address",status=401)
#             existing_interns = Intern.objects.filter(email=request.data['email'])
#             if len(existing_interns)>1:
#                 return Response("Many users with email "+serializer.data['email'],status=402)
#             if len(existing_interns)==1:
#                 return Response(serializer.data, status=201)
#             serializer.save()
#             return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)
    
    def put(self, request, pk, format=None):
        Intern = self.get_object(pk)
        serializer = InternSerializer(User, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        intern = self.get_object(pk)
        intern.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InternRoles(APIView):
    def get_intern_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get_department_object(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        intern = self.get_intern_object(pk)
        depRoleList = DepartmentInternRoleList.objects.filter(user=intern)
        if depRoleList.count()>1:
            depRoleListSer=DepartmentInternRoleListSerializer(data=depRoleList,many=True)
        else:
            depRoleListSer=DepartmentInternRoleListSerializer(data=depRoleList.values())
        if depRoleListSer.is_valid():
            return Response(depRoleListSer.data)
        raise Http404
    
    def put(self,request,pk):
        internObj = self.get_intern_object(pk)
        depObj = self.get_department_object(request.data.get('dep_id',None))
        role_list = list(map(int,request.POST.getlist('role_list')))
        depRoles = depObj.rolesList.all().values_list('role_id',flat=True)
        legal_roles=[]
        for role_id in role_list:
            if (role_id in depRoles):
                legal_roles.append(role_id)
        internCurrRoles = DepartmentInternRoleList.objects.filter(department_id=depObj.pk,user=internObj).values_list('role_id', flat=True)
        addedObjs=[]
        for role in legal_roles:
            if not (role in internCurrRoles):                
                depIntRoleSer = DepartmentInternRoleListSerializer(data={'department_id':depObj.pk,'user':internObj.pk,'role_id':role})
                depIntRoleSer.is_valid(raise_exception=True)
                depIntRoleSer.save()
                addedObjs.append(role)
        return Response(json.dumps({"data":addedObjs}), content_type='application/json', status=201)

#     def delete(self,request,pk):
#         if (not 'day' in request.data) or (not 'type' in request.data) or (not 'user' in request.data):
#             return Response({'Fail':'Missing mandatory post variables - day/type/user'},status=Http404)
#         dayLimitObj = self.get_day_limit_object(request.data['day'], request.data['type'], request.data['user'])
#         if dayLimitObj.is_valid():
#             dayLimitObj.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=Http404)

class InternScheduleLimitations(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get_duty_limit_object(self, restriction_type):
        try:
            return DutyLimit.objects.get(pk=restriction_type)
        except User.DoesNotExist:
            raise Http404

    def get_day_limit_object(self, day,type,user,dep_id):
        try:
            return DayLimit.objects.filter(date=day,Intern=user,limit=type,department=dep_id)
        except User.DoesNotExist:
            raise Http404
    
    def get(self,request,pk):
        internLimits = DayLimit.objects.filter(intern__pk=int(pk))
        if not internLimits.count():
            return Response({"Fail":"Intern "+pk+" has no assigned duty limits."},status=Http404)
        internSer = DayLimitSerializer(internLimits,many=True)
        return Response(internSer.data) 
        
    def post(self, request, pk):
        limitations_list = request.data.get('limitations_list',None)
        dep_id = request.data.get('dep_id',None)
        if not limitations_list or not dep_id:
            return Response({"Fail":"limitation list or department id is not provided."},status=Http404)
        intern = self.get_object(pk)
        addedObjs = []
        for limitation in limitations_list:
            date = limitation.get('date')
            limit_type = limitation.get('type')
            dlSerializer = DayLimitSerializer(data={'date':date,'limit':limit_type,'intern':intern.user,'department':dep_id})
            if dlSerializer.is_valid():
                dlSerializer.save()
                addedObjs.append(date)
        return Response(json.dumps({"data":addedObjs}), content_type='application/json', status=201)
    
    def delete(self,request,pk):
        if (not 'day' in request.data) or (not 'type' in request.data) or (not 'user' in request.data) or (not 'dep_id' in request.data):
            return Response({'Fail':'Missing mandatory post variables - day/type/user/dep_id'},status=Http404)
        dayLimitObj = self.get_day_limit_object(request.data['day'], request.data['type'], request.data['user'],request.data['dep_id'])
        if dayLimitObj.is_valid():
            dayLimitObj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=Http404)

####################################
#
#    Department
#
####################################

class DepartmentRoles(APIView):
    def get_object(self, pk):
        try:
            return Department.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    def get(self,request,pk):
        depObj = self.get_object(pk)
        ser = DepartmentSerializer(depObj)
        return Response(ser.data)
    
    def check_roles(self,roles):
        if not roles:
            raise Response({'Fail':'The roles are empty for edit'},status.HTTP_404_NOT_FOUND)
        roleObjs = Role.objects.filter(role_id__in=roles)
        if not roleObjs:
            raise Response({'Fail':'Roles dont exist in DB'},status.HTTP_404_NOT_FOUND)
        return roleObjs
    
    def put(self,request,pk):
        depObj = self.get_object(pk)
        roles = request.POST.getlist('roles_list')
        roleObjs = self.check_roles(roles)
        depObj.rolesList.set(roleObjs)
        return Response(request.data,status=status.HTTP_202_ACCEPTED)
#         depSer = DepartmentSerializer(depObj)
#         if depSer.is_valid():
#             return Response(depSer.data)
        
# class DepartmentLimits(APIView):
#     def get_object(self, pk):
#         try:
#             return Department.objects.get(pk=pk)
#         except Intern.DoesNotExist:
#             raise Http404
#     def get(self,request,pk):
#         depObj = self.get_object(pk)
#         ser = DepartmentSerializer(depObj)
#         return Response(ser.data)
#     
#     def check_limits(self,limits):
#         if not limits:
#             raise Response({'Fail':'The limits are empty for edit'},status.HTTP_404_NOT_FOUND)
#         limitObjs = DutyLimit.objects.filter(limit_id__in=limits)
#         if not limitObjs:
#             raise Response({'Fail':'limits dont exist in DB'},status.HTTP_404_NOT_FOUND)
#         return limitObjs
#     
#     def put(self,request,pk):
#         depObj = self.get_object(pk)
#         limits = request.POST.getlist('limit_list')
#         roleObjs = self.check_limits(limits)
#         depObj..set(roleObjs)
#         return Response(request.data,status=status.HTTP_202_ACCEPTED)


class DepartmentView(APIView):
    def get_object(self,pk):
        try:
            return Department.objects.get(pk=pk)
        except:
            raise Response({'Fail':'Department doesnt exist'},Http404)
        
    def get_intern(self,user):
        try:
            return User.objects.get(pk=user)
        except:
            raise Response({'Fail':'intern doesnt exist'},Http404)
    
    def get_admin_role(self):
        try:
            return Role.objects.get(role=ADMIN)
        except:
            raise Response({'Fail':'Role admin doesnt exist'},Http404)
        
    def get(self,request):
        deps = Department.objects.all()
        ser = DepartmentSerializer(deps,many=True)
        return Response(ser.data)

    def post(self,request):
        dep_name = request.data.get('name',None)
        user = request.data.get('admin_intern_id',None)
        if not dep_name or not user:
            raise Response({'Fail':'Miissing name for new department'},status=404)
        internObj = self.get_intern(user)
        admin_role = self.get_admin_role()
        depSer = DepartmentSerializer(data={'name':dep_name,'InternsList':[user],'rolesList':[admin_role.pk]})        
        if depSer.is_valid():
            depSer.save()
            depInternRoleSer = DepartmentInternRoleListSerializer(data={'department_id':depSer.data['department_id'],'user':user,'role_id':admin_role.pk})
            if depInternRoleSer.is_valid():
                depInternRoleSer.save()                
                return Response(depSer.data,status=201)
            depSer.delete()
            return Response({'Fail':'Failed creating new department, with params parsing and update'},status=404)
        return Response({'Fail':'Failed creating new department'},status=404)
    def delete(self,request):
        dep_id = request.data.get('id',None)
        depObj = self.get_object(dep_id)
        depObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class DepartmentInternsList(APIView):
    def get_object(self, pk):
        try:
            return Department.objects.filter(InternsList__username=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        department = self.get_object(pk)
        if not department:
            return Response(data=[],status=201)
        serializer = DepartmentSerializer(department,many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        
####################################
#
#    Roles
#
####################################

class RoleList(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

        
class DutyLimitView(APIView):
    def get(self,request):
        dutyLimitObjs = DutyLimit.objects.all()
        dutyLimitSer = DutyLimitSerializer(dutyLimitObjs,many=True)
        return Response(dutyLimitSer.data)
    
    def post(self,request):
        serializer = DutyLimitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

        
        

####################################
#
#    Scheduler
#
####################################

class SchedulerView(APIView):
    def get_dep_obj(self,pk):
        try:
            return Department.objects.get(pk=pk)
        except Department.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
            
    def get(self,request,pk):
        pass
    
    def post(self,request,pk):
        depObj = self.get_dep_obj(pk)
        month = request.data.get('month',None)
        year = request.data.get('year',None)
        if not month or not year:
            return Response(exception=Exception({'Fail':'Please provide month and year to schedule for'}),status=status.HTTP_400_BAD_REQUEST)
        schedObj = DutySchedule(depObj.department_id,int(month),int(year))
        days = DutySchedule.runScheduler(schedObj.mDays, schedObj)
        daysCal = ScheduleCalendar(days)
        htmlStr = daysCal.formatmonth(int(year),int(month))
        
        return HttpResponse(htmlStr)

def logout_view(request):
    logout(request)
    return HttpResponse(status=200)

# class PlayerDetail(APIView):
#     """
#     Retrieve, update or delete a Player instance.
#     """
#     def get_object(self, pk):
#         try:
#             return Player.objects.get(pk=pk)
#         except Player.DoesNotExist:
#             raise Http404
# 
#     def get(self, request, pk, format=None):
#         Player = self.get_object(pk)
#         serializer = PlayerSerializer(Player)
#         return Response(serializer.data)
# 
#     def put(self, request, pk, format=None):
#         Player = self.get_object(pk)
#         serializer = PlayerSerializer(Player, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
#     def delete(self, request, pk, format=None):
#         Player = self.get_object(pk)
#         Player.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
# 
# class TeamsList(APIView):
#     def get(self, request, format=None):
#         teams = Team.objects.all()
#         serializer = TeamSerializer(teams, many=True)
#         return Response(serializer.data)
# 
#     def post(self, request, format=None):
#         serializer = TeamSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
# class CourtList(APIView):
#     def get(self, request, format=None):
#         courts = Court.objects.all()
#         serializer = CourtSerializer(courts, many=True)
#         return Response(serializer.data)
# 
#     def post(self, request, format=None):
#         serializer = CourtSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# 
# 
# class GameList(APIView):
#     def get(self, request, format=None):
#         games = Game.objects.all()
#         serializer = GameSerializer(games, many=True)
#         return Response(serializer.data)
# 
#     def post(self, request, format=None):
#         serializer = GameSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     


