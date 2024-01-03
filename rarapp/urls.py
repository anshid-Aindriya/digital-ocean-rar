from django.urls import path
from rarapp import views 
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    
    path('register/', views.register, name='register'),
    path('register-success/', views.registrationSuccess, name='register-success'),
    path('login/', views.login, name='login'),
    path('forgot-password/',views.forgotPassword,name='forgot-password'),
    path('reset-password/<token>/', views.resetPassword, name='reset-password'),
    path('logout/', views.logout, name='logout'),

    
    path('add-user/', views.addUser, name='add-user'),
    path('get-user-data/',views.get_user_data, name='get-user-data'),
    path('update-user/', views.update_user, name='update-user'),
    path('user-delete/', views.deleteUser, name='user-delete'),
  
    path('',views.dashboard,name='dashboard' ),
    path('main/<int:project_id>/',views.mainLayouts,name='main'),

    path('add-project/',views.addProject,name='add-project'),
    path('project-delete/',views.deleteProject,name='project-delete'),
    path('get-project-data/',views.get_project_data,name='get-project-data'),
    path('update-project/', views.update_project, name='update-project'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('autocomplete-users/', views.autocomplete_users, name='autocomplete-users'),
   
    path('add-timesheet/',views.addTimesheet,name='add-timesheet'),
    path('timesheet/',views.timesheet_view,name='timesheet'),
    path('timesheet-delete/', views.deleteTimesheet, name='timesheet-delete'),
    path('edit-timesheet/<int:timesheet_id>/', views.editTimesheet, name='edit-timesheet'),
    path('get_users_for_project/<int:project_id>/', views.get_users_for_project, name='get_users_for_project'),

    path('allotment/<int:project_id>/',views.Allotment,name='allotment'),
    path('update-allotment/', views.update_allotment, name='update-allotment'),
    path('delete-allotment/<int:allotment_id>/', views.delete_allotment, name='delete_allotment'),
    path('delete-allotment-user/<int:allotment_id>/<int:user_id>/',views.delete_allotment_user, name='delete_allotment_user'),
    
    path('milestone/<int:project_id>/',views.milestones,name='milestone'),
    path('fetch_milestone_data/', views.fetch_milestone_data, name='fetch_milestone_data'),
    path('update_milestone/', views.update_milestone, name='update_milestone'),
    path('delete-milestone/', views.delete_milestone, name='delete-milestone'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)