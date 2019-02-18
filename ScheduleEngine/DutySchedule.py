'''
Created on Mar 5, 2018

@author: lkuznets
'''

from random import randint
from tkinter import getint
from scheduler.models import *
import calendar
from datetime import *
import operator

class DutySchedule:
#     interns = {'Mord':[6,7,20,23,24,28],'YuliaV':[15,16,17,18,19,20,21,22,23,24,25,26,27,28,2],
#                'Bashir':[5,6,12,13,19,20,26,27],'Jenny':[],'Haled':[6,7,15,20],'Sveta':[1,2,3,4,5,11,12,13,16,17,25,26,27],
#                'Kleir':[5,7,12,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],'Rula':[6,13,16,17,20,27],
#                'Narmin':[1,2,3,4,5,6,7,8,9,10,11,22,23,24],'Rana':[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,26,27],
#                'Einav':[20,21,28],'Shlomit':[20,21,28],'YuliaB':[27],'Dana':[12,27],
#                'Husein':[1,6,7,22,23,28],'Amer':[1,9,10,11,18,19,21,22,23,27,28]}
#     
#     Miun = ['Mord','YuliaV','Bashir','Jenny','Haled','Sveta','Kleir','Rana','Rula']
#     
#     Pagia = ['Mord','YuliaV','Bashir','Jenny','Haled','Kleir','Rula']
#     
#     Mahlaka = ['Einav','Shlomit','YuliaB','Dana','Husein','Amer']
         
    MAX_DUTIES_DIFF=1
    
    def __init__(self,department_id,month,year,firstWeekDay=6):
        self.depObj = Department.objects.get(pk=department_id)
        self.depInternRolesList = DepartmentInternRoleList.objects.filter(department_id=department_id)
        roles = self.depObj.rolesList.all()
        self.roleObjs = Role.objects.filter(role_id__in=roles)
        self.depRoleDict = {}
        self.mMonth = int(month)
        self.mYear = int(year)
        self.internShifts = {}
        for roleObj in self.roleObjs:
            self.depRoleDict[roleObj.role_id] = []
        for depInternRole in self.depInternRolesList:
            intern_id=depInternRole.intern_id.intern_id
            role_id=depInternRole.role_id.role_id
            role_type = depInternRole.role_id.role
            if int(role_type) == ADMIN:
                continue
            self.depRoleDict[role_id].append(intern_id)
        self.depInternLimitList = DayLimit.objects.filter(department=department_id).filter(date__year=year,date__month=month)
        self.internLimits = {}
        for depInternLimit in self.depInternLimitList:
            intern_id = depInternLimit.intern.intern_id
            limit_id = depInternLimit.limit.limit_id
            date = depInternLimit.date
            if not intern_id in self.internLimits:
                self.internLimits[intern_id]={'date':[date],'limit':[limit_id]}
            else:
                self.internLimits[intern_id]['date'].append(date)
                self.internLimits[intern_id]['limit'].append(limit_id)
        self.mDays={}
        self.dayType={}
        cal = calendar.Calendar()
        cal.setfirstweekday(firstWeekDay)
        month_days = cal.itermonthdays(self.mYear, self.mMonth)
        for ind, day in enumerate(month_days):
            if not day:
                continue
            self.mDays[day] = None            
            self.dayType[day] = ind%7
        return
    
    def getIntern(self,day,intList):
        legalInterns = []
        for intern in intList:
            if day not in self.interns[intern]:
                legalInterns.append(intern)
        j=randint(0,len(legalInterns)-1)
#         print("got {0} of {1} objects".format(j,len(legalInterns)))
        return(legalInterns[j])
    
    def getLegalInterns(self,day,role):
        legalInterns = []
        roleInterns = self.depRoleDict[role]
        for intern in roleInterns:
            internDayLimits = self.internLimits[intern]
            dt = date(self.mYear,self.mMonth,day)
            if dt in internDayLimits['date']:
                continue
            legalInterns.append(intern)
        return legalInterns
    
    def createDay(self,day,dayObjList,depth):
        chosenInterns = {}
        usedInterns = []
        for dayObj in dayObjList:
            if not dayObj:
                continue
            dayInterns = dayObj.roleInternDict.values()
            usedInterns+=dayInterns
        for role in self.depRoleDict.keys():
            legalInterns = self.getLegalInterns(day,role)
            for attempt in range(100):
                j=randint(0,len(legalInterns)-1)
                if legalInterns[j] in usedInterns:
                    continue
                chosenInterns[role]=legalInterns[j]
                usedInterns.append(legalInterns[j])
                break
        if len(chosenInterns.keys())!=len(self.depRoleDict.keys()):
#             print("-E- Failed finding interns for day {day}, avalaible interns {interns}, at depth {depth}".format(day=day,interns=chosenInterns,depth=depth))
            return None
        return DutySchedule.Day(day,chosenInterns)


    def getDayType(self,date):
        dayWeekType=self.dayType[date]
        if dayWeekType>=0 and dayWeekType<=4:
            return REGULAR
        else:
            return WEEKEND
    
    @staticmethod
    def sortByDuties(schedObj,legalInterns,days,date):
        legalInternsDict = {}
        dateType = schedObj.getDayType(date)
        for intern in legalInterns:
            legalInternsDict[intern]=0
        for dayKey in days.keys():
            day=days[dayKey]
            if day:
                tmpDayType = schedObj.getDayType(day.mDay)
                for intern in day.getDayInterns():
                    if intern in legalInterns and tmpDayType == dateType:
                        legalInternsDict[intern]+=1
        sortedObjs = sorted(legalInternsDict.items(), key=operator.itemgetter(1))
        sortedInterList = []
        if len(sortedObjs)>0:
            minDuties=sortedObjs[0][1]
        for sortedObj in sortedObjs:
            currDuties=sortedObj[1]
            if (currDuties-minDuties)>=schedObj.MAX_DUTIES_DIFF:
                break
            sortedInterList.append(sortedObj[0])
        return sortedInterList
    
    @staticmethod
    def checkDayAtempt(schedObj,randDay,days,depth):
        prevDay=days.get(randDay-1,None)
        #prevPrevDay=days.get(randDay-2,None)
        nextDay=days.get(randDay+1,None)
        #nextNextPrevDay=days.get(randDay+2,None)
        # When creating new day, choose only possible interns that did not participated in previous days.
        #newDayObj = schedObj.createDay(randDay,,depth)
        chosenInterns = {}
        usedInterns = []
        #for dayObj in [prevDay,prevPrevDay,nextDay,nextNextPrevDay]:
        for dayObj in [prevDay,nextDay]:
            if not dayObj:
                continue
            dayInterns = dayObj.roleInternDict.values()
            usedInterns+=dayInterns
        for role in schedObj.depRoleDict.keys():
            legalInterns = schedObj.getLegalInterns(randDay,role)
            legalInternsSorted = DutySchedule.sortByDuties(schedObj,legalInterns,days,randDay)
            for intern in legalInternsSorted:
                if intern in usedInterns:
                    continue
                chosenInterns[role]=intern
                usedInterns.append(intern)
                break
        if len(chosenInterns.keys())!=len(schedObj.depRoleDict.keys()):
#             print("-E- Failed finding interns for day {day}, avalaible interns {interns}, at depth {depth}".format(day=randDay,interns=chosenInterns,depth=depth))
            return None
        return DutySchedule.Day(randDay,chosenInterns)
            
    
    def printDaysToCsv(self,days):
        for day in days:
            print(day)
        return
    
    @staticmethod
    def avaliableDays(daysDict):
        avaliableDays = []
        for day in daysDict:
            if not daysDict[day]:
                avaliableDays.append(day)
        return avaliableDays
    
    @staticmethod
    def randSelectAvaliableDay(daysDict):
        avaliableDays = []
        for day in daysDict:
            if not daysDict[day]:
                avaliableDays.append(day)
        if not len(avaliableDays):
            return None
        j=randint(0,len(avaliableDays)-1)
        return avaliableDays[j]
    
    @staticmethod
    def runScheduler(days,schedObj,depth=0):
        new_days=days.copy()
        avaliableDays = DutySchedule.avaliableDays(new_days)
        while len(avaliableDays):
            j=randint(0,len(avaliableDays)-1)
            avaliableDay = avaliableDays[j]
            day = DutySchedule.checkDayAtempt(schedObj,avaliableDay,new_days,depth)
            if day == None:
                avaliableDays.pop(j)
                if len(avaliableDays)==0:
                    return None
                continue
            new_days[avaliableDay]=day
            newDays = DutySchedule.runScheduler(new_days, schedObj,depth+1)
            if newDays == None:
                avaliableDays.pop(j)
                continue
            else:
                return newDays
        #Lets check all days are fullfiled
        avaliableDays = DutySchedule.avaliableDays(new_days)
        if len(avaliableDays)==0:
            return new_days
        # Failed creating a recursive day so far
        return None
    
    class Day():
        def __init__(self,date,roleInternDict):
            self.mDay=date
            self.roleInternDict=roleInternDict
        
        def compareToDay(self,otherDay):
            for role in self.roleInternDict.keys():
                roleIntern = self.roleInternDict[role]
                for otherDayRole in otherDay.roleInternDict.keys():
                    if roleIntern == otherDay.roleInternDict[otherDayRole]:
                        return False
            return True
        
        def getDayInterns(self):
            internList = []
            for role in self.roleInternDict.keys():
                internList.append(self.roleInternDict[role])
            return internList
                 
        def __str__(self):
            return "{0},{1}".format(self.mDay,self.roleInternDict)

