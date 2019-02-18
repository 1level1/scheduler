from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# from pygments.lexers import get_all_lexers
# from pygments.styles import get_all_styles

# LEXERS = [item for item in get_all_lexers() if item[1]]
# LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
# STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

ER = 0
NICU = 1
DEPARTMENT = 2
ADMIN = 3
WEEKEND=0
HOLLIDAY=1
REGULAR=2
OTHER=3

ROLES = (
    (ER,'ER'),
    (NICU,'NICU'),
    (DEPARTMENT,'Department'),
    (ADMIN,'ADMIN'),
)
DAY_TYPE = (
    (WEEKEND,'WEEKEND'),
    (HOLLIDAY,'HOLIDAY'),
    (REGULAR,'REGULAR'),
    (OTHER,'OTHER'),
)
LIMIT_TYPE = (
    ('0', 'RED'),
    ('1','YELLOW'),
    ('2','GREEN'),
)

class DutyLimit(models.Model):
    limit_id = models.CharField(choices=LIMIT_TYPE, max_length=100,primary_key=True)
    class Meta:
        ordering = ('limit_id','limit_id')

class DayLimit(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField()
    limit = models.ForeignKey('DutyLimit',on_delete=models.CASCADE)
    intern = models.ForeignKey(User,on_delete=models.CASCADE)
    department = models.ForeignKey('Department',on_delete=models.CASCADE)
    class Meta:
        ordering = ('id','date')
        
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role = models.CharField(choices=ROLES, max_length=100)
    roleRestrictions = models.CharField(default='',max_length=100)
    class Meta:
        ordering = ('role_id','role')
        

class Day(models.Model):
    day_id = models.AutoField(primary_key=True)
    date = models.DateField()
    type = models.CharField(choices=DAY_TYPE, max_length=100)
    interns = models.ManyToManyField(User)
    roles = models.ForeignKey(Role,on_delete=models.CASCADE)
    class Meta:
        ordering = ('day_id','date','type')
    
class Schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    days = models.ManyToManyField(Day)
    class Meta:
        ordering = ('schedule_id','schedule_id')
    
    
class Department(models.Model):   
    department_id = models.AutoField(primary_key=True)
    name = models.TextField()
    rolesList = models.ManyToManyField(Role)
    InternsList = models.ManyToManyField(User, related_name="Users")
    schedules = models.ManyToManyField(Schedule,blank=True)
    class Meta:
        ordering = ('department_id','name')

class DepartmentInternRoleList(models.Model):
    id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    role_id = models.ForeignKey(Role,on_delete=models.CASCADE)
    class Meta:
        ordering = ('id','department_id','user','role_id')