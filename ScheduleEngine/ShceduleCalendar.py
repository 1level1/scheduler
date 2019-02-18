'''
Created on Mar 12, 2018

@author: lkuznets
'''

from calendar import SUNDAY,HTMLCalendar
from scheduler.models import  User
intern_colors = ((0,"#F73208"),
               (1,"#322C2A"),
               (2,"#C73208"),
               (3,"#A43208"),
               (4,"#3F3208"),
               (5,"#AA3208"),
               (6,"#EE3208"),
               (7,"#083208"),
               (8,"#AD3208"),
               (9,"#CD3208"),
               (10,"#BE3208"),
               (11,"#EB1865"),
               (12,"#B5F310"),
               (13,"#43F310"),
               (14,"#10B5F3"),               
               (15,"#10F3C0"),
               (16,"#F3C010"),
               (17,"#105CF3"),
               (18,"#10CDF3"),
               )
class ScheduleCalendar(HTMLCalendar):
    def __init__(self,dayObjectsList):
        self.mdayObjectsList = dayObjectsList
        super().__init__(SUNDAY)
        self.mInterns = {}
        for internObj in User.objects.all():
            self.mInterns[internObj.intern_id] = internObj.name            

    def formatday(self, day, weekday):
        """
          Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            dayInterns = self.mdayObjectsList[day].roleInternDict
            internsHtml = ""
            for role in dayInterns.keys():
                intern_id = dayInterns[role]
                internsHtml += "<p style=\"color:{color};\">{intern_id}</p>".format(color=intern_colors[intern_id%18][1],intern_id=self.mInterns[intern_id])
            tryHtml = '<td class="%s"><a href="%s">%d</a>%s</td>' % (self.cssclasses[weekday], weekday, day,internsHtml) 
            return tryHtml  
