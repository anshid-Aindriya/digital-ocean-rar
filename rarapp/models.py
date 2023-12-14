from django.db import models

class admin_db(models.Model):
    name              = models.CharField(max_length=100, default='')
    email             = models.CharField(max_length=100, default='')
    password          = models.CharField(max_length=100, default='')
    created_at        = models.DateTimeField(max_length=100, default='')
    updated_at        = models.DateTimeField(max_length=100, default='')
    reset_token       = models.CharField(max_length=100, default='')

class manager_db(models.Model):
    name              = models.CharField(max_length=100, default='')
    email             = models.CharField(max_length=100, default='')
    password          = models.CharField(max_length=100, default='')
    created_at        = models.DateTimeField(max_length=100, default='')
    updated_at        = models.DateTimeField(max_length=100, default='')
    reset_token       = models.CharField(max_length=100, default='')
 
   
class user_db(models.Model):
   name               = models.CharField(max_length=100,default='',null=True)
   email              = models.CharField(max_length=100,default='',null=True)
   position           = models.CharField(max_length=100,default='',null=True)
   profile_image      = models.ImageField(upload_to='image',null=True)
   created_at         = models.CharField(max_length=100,default='')
   updated_at         = models.CharField(max_length=100,default='')
   
class project_db(models.Model):
   users              = models.ManyToManyField(user_db) 
   title              = models.CharField(max_length=100,default='',null=True)
   start_date         = models.CharField(max_length=100,default='',null=True)
   due_date           = models.CharField(max_length=100,default='',null=True)
   total_hrs          = models.CharField(max_length=100,default='',null = True)
   progress           = models.CharField(max_length=100,default='',null = True)
   random_color       = models.CharField(max_length=100,default='',null = True)
   is_favorite        = models.BooleanField(default=False)
   created_at         = models.CharField(max_length=100,default='')
   updated_at         = models.CharField(max_length=100,default='')

class timesheet_db(models.Model):
   user               = models.ForeignKey(user_db, on_delete=models.CASCADE, default=None, null=True)
   project            = models.ForeignKey(project_db, on_delete=models.CASCADE, default=None, null=True)
   worked_time        = models.CharField(max_length=100, default='', null=True)
   date               = models.DateField(default=None, null=True)
   created_at         = models.DateTimeField(auto_now_add=True)
   updated_at         = models.DateTimeField(auto_now=True)

class allotment_db(models.Model): 
   project            = models.ForeignKey(project_db,on_delete=models.CASCADE,default='',null=True)
   status             = models.CharField(max_length=100,default='PENDING')
   created_at         = models.CharField(max_length=100,default='')
   updated_at         = models.CharField(max_length=100,default='')

class allotment_user_db(models.Model): 
   user               = models.ForeignKey(user_db,on_delete=models.CASCADE,default='',null=True)
   allotment          = models.ForeignKey(allotment_db,on_delete=models.CASCADE,default='',null=True)
   user_time          = models.CharField(max_length=100,default='',null=True)
   user_alloted       = models.CharField(max_length=100,default='',null=True)
   created_at         = models.CharField(max_length=100,default='')
   updated_at         = models.CharField(max_length=100,default='')

class milestone_db(models.Model):
    project           = models.ForeignKey(project_db, on_delete=models.CASCADE, default=None, null=True)
    title             = models.CharField(max_length=100, default='', null=True)
    release_date      = models.DateField(default=None, null=True)
    expected_date     = models.DateField(default=None, null=True)
    actual_date       = models.DateField(default=None, null=True)
    completed_tasks   = models.PositiveIntegerField(default=0)  
    total_tasks       = models.PositiveIntegerField(default=0)      
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)