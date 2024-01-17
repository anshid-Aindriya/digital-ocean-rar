from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
import uuid, re, json, calendar, random
from rarapp.models import *
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from datetime import timedelta
from django.urls import reverse
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def register(request):
    if request.method == "POST":
        name          = request.POST["name"]
        email         = request.POST["email"]
        position      = request.POST["position"]
        password1     = request.POST["password1"]
        password2     = request.POST["password2"]
        date          = datetime.now()

        if password1     == password2:
            if position  == "Admin":
                admin_db.objects.create(
                    name        = name,
                    email       = email,
                    password    = password1,
                    created_at  = date,
                    updated_at  = date
                )

            elif position   == "Project Manager":
                manager_db.objects.create(
                    name        = name,
                    email       = email,
                    password    = password1,
                    created_at  = date,
                    updated_at  = date
                )

            return redirect("register-success")

    return render(request, "register.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.method  == "POST":
        email           = request.POST["email"]
        password        = request.POST["password"]

        admin_user      = admin_db.objects.filter(email=email, password=password).first()

        manager_user    = manager_db.objects.filter(email=email, password=password).first()

        if admin_user:
            request.session["adminId"]    = admin_user.id
            request.session["Name"]       = admin_user.name

            return redirect("dashboard")

        elif manager_user:
            request.session["managerId"]   = manager_user.id
            request.session["Name"]        = manager_user.name

            return redirect("dashboard")

        else:
            messages.error(request, "Invalid username or password")

            return redirect("login")
    else:
        if request.session.get("adminId"):
            return redirect("dashboard")

        elif request.session.get("managerId"):
            return redirect("dashboard")

        else:
            return render(request, "login.html")


def send_forgot_password_mail(request, user, token):
    current_site     = get_current_site(request)
    domain           = current_site.domain

    subject          = "Your Forget Password Link"
    reset_link       = f"http://{domain}/reset-password/{token}/"
    message          = f"Hi {user.name},\n\nHere is your password reset link: {reset_link}"

    email_from       = settings.EMAIL_HOST_USER
    recipient_list   = [user.email]

    send_mail(subject, message, email_from, recipient_list)


def forgotPassword(request):
    if request.method == "POST":
        email            = request.POST.get("email")
        admin_obj        = admin_db.objects.filter(email=email).first()

        if not admin_obj:
            manager_obj  = manager_db.objects.filter(email=email).first()
            if not manager_obj:

                messages.error(request, "No user found with this email.")
                return redirect("forgot-password")

            token                     = str(uuid.uuid4())
            manager_obj.reset_token   = token
            manager_obj.save()

            send_forgot_password_mail(request, manager_obj, token)

            messages.success(request, "An email was sent successfully")

            return redirect("forgot-password")

        token                   = str(uuid.uuid4())
        admin_obj.reset_token   = token
        admin_obj.save()
        send_forgot_password_mail(request, admin_obj, token)

        messages.success(request, "An email was sent successfully")

        return redirect("forgot-password")

    return render(request, "forgot_password.html")


def resetPassword(request, token):
    context              = {}
    try:
        admin_obj        = admin_db.objects.filter(reset_token=token).first()
        manager_obj      = None

        if not admin_obj:
            manager_obj  = manager_db.objects.filter(reset_token=token).first()

        if not admin_obj and not manager_obj:
            messages.error(request, "Invalid token")
            return redirect("login")

        if request.method      == "POST":
            new_password       = request.POST.get("password")
            confirm_password   = request.POST.get("confirm_password")
            user_id            = admin_obj.id if admin_obj else manager_obj.id

            if new_password    != confirm_password:
                messages.error(request, "Passwords do not match")
                return redirect(reverse("reset-password", args=[token]))

            user               = admin_obj if admin_obj else manager_obj
            user.password      = new_password
            user.reset_token   = ""
            user.save()

            messages.success(request, "Password changed successfully")
            return redirect("login")

        context["user_id"]     = admin_obj.id if admin_obj else manager_obj.id

    except Exception as e:
        messages.error(request, "An error occurred")
        print(e)

    return render(request, "password_reset.html", context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrationSuccess(request):
    return render(request, "registration-success.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout(request):
    if request.session.get("adminId"):
        del request.session["adminId"]

    if request.session.get("managerId"):
        del request.session["managerId"]

    return redirect("login")


def calculate_remaining_days(start_date, due_date, current_date):
    remaining_days = (due_date - current_date).days
    return remaining_days


def dashboard(request):
    if "adminId" in request.session or "managerId" in request.session:
        users                = user_db.objects.all()
        all_project_details  = project_db.objects.all().annotate(
            user_count       = Count("users")
        )

        show_favorites       = request.GET.get("show_favorites")

        if show_favorites   == "true":
            project_details  = project_db.objects.filter(is_favorite=True)

        else:
            project_details  = all_project_details

        formatted_projects   = []
        current_date         = datetime.now()
        current_day_name     = calendar.day_name[current_date.weekday()]

        for project in project_details:
            if isinstance(project.created_at, str):
                created_at   = datetime.strptime(
                    project.created_at, "%Y-%m-%d %H:%M:%S.%f"
                )
            else:
                created_at          = project.created_at

            start_date              = datetime.strptime(project.start_date, "%Y-%m-%d")
            due_date                = datetime.strptime(project.due_date, "%Y-%m-%d")

            formatted_created_at    = created_at.strftime("%B %d, %Y")
            formatted_start_date    = start_date.strftime("%b %d, %Y")
            formatted_due_date      = due_date.strftime("%b %d, %Y")
            formatted_created_time  = created_at.strftime("%I:%M %p")

            project.formatted_created_time  = formatted_created_time
            project.formatted_created_at    = formatted_created_at
            project.formatted_start_date    = formatted_start_date
            project.formatted_due_date      = formatted_due_date
            remaining_days   = calculate_remaining_days(
                start_date, due_date, current_date
            )
            project.remaining_days   = remaining_days

            overdue                  = False

            if remaining_days    < 0:
                if remaining_days       == -1:
                    additional_message  = "Today is overdue"

                else:
                    additional_message  = f"{abs(remaining_days) - 1} day{'s' if abs(remaining_days) != -1 else ''} overdue"
                    overdue             = True

            elif remaining_days  == 0:
                additional_message      = "Today is due date"
                overdue                 = False
            else:
                additional_message  = (
                    f"{remaining_days} day{'s' if remaining_days > 1 else ''} remaining"
                )
                overdue                 = False

            project.additional_message  = additional_message
            project.overdue             = overdue

            formatted_projects.append(project)

        context =  {

                     "user_data": users,
                     "project_data": formatted_projects,
                     "current_date": current_date,
                     "day_name": current_day_name

                   }

        return render(request, "index.html", context)
    else:
        return render(request, "login.html")


def addUser(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method == "POST":
            name            = request.POST.get("name")
            email           = request.POST.get("email")
            position        = request.POST.get("position")
            profile_image   = request.FILES.get("profile_image")
            date            = datetime.now()

            if profile_image:
                new_user            = user_db(
                    name            = name,
                    email           = email,
                    profile_image   = profile_image,
                    position        = position,
                    created_at      = date,
                    updated_at      = date
                )

            else:
                new_user = user_db(
                    name       = name,
                    email      = email,
                    position   = position,
                    created_at = date,
                    updated_at = date
                )

            new_user.save()

            messages.success(request, "User successfully added.")
            return redirect("dashboard")

        users = user_db.objects.all().order_by("name")

        context = {
            "user_data": users
        }

        return render(request, "index.html", context)
    else:
        return render(request, "login.html")


def get_user_data(request):
    if request.method  == "GET":
        user_id        = request.GET.get("user_id")
        try:
            user       = get_object_or_404(user_db, id=user_id)

            user_data  = {
                
                           "name"            : user.name,
                           "email"           : user.email,
                           "position"        : user.position,
                           "profile_image"   : user.profile_image.url if user.profile_image else None

                         }

            return JsonResponse(user_data)

        except user_db.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


def update_user(request):
    if request.method   == "POST":
        user_id         = request.POST.get("user_id")
        name            = request.POST.get("name")
        email           = request.POST.get("email")
        position        = request.POST.get("position")
        profile_image   = request.FILES.get("profile_image")

        try:
            user     = user_db.objects.get(id=user_id)
            user.name       = name
            user.email      = email
            user.position   = position

            if profile_image:
                user.profile_image  = profile_image

            user.save()
            messages.success(request, "Successfully updated")

        except user_db.DoesNotExist:
            messages.error(request, "No User Found")

    return redirect("dashboard")


def deleteUser(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method   == "POST":
            user_id         = request.POST.get("id")

            if user_id:
                user_data   = user_db.objects.filter(id=user_id)

                if user_data.exists():

                    user_data.delete()
                    messages.success(request, "Successfully Deleted.")
                else:
                    messages.error(request, "User not found.")
            else:
                messages.error(request, "Invalid user ID.")

            return redirect("dashboard")
    else:
        return render(request, "login.html")




def autocomplete_users(request):
    if "adminId" in request.session or "managerId" in request.session:
        query        = request.GET.get("q", "")
        users        = user_db.objects.filter(name__icontains=query)[:10]
        users_list   = [
            {

             "id"   : user.id,
             "name" : user.name

            } for user in users

            ]
        return JsonResponse(users_list, safe=False)
    else:
        return render(request, "login.html")


def generate_random_color():
    r     = random.randint(0, 255)
    g     = random.randint(0, 255)
    b     = random.randint(0, 255)
    return f"rgb({r},{g},{b})"


def addProject(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method    == "POST":
            try:
                title          = request.POST.get("title")
                start_date     = request.POST.get("start_date")
                due_date       = request.POST.get("due_date")
                total_hours    = request.POST.get("total_hours")
                date           = datetime.now()

                selected_user_ids  = request.POST.getlist("selected_users")
     
                random_color       = generate_random_color()

                project_data = project_db(
                    title         = title,
                    start_date    = start_date,
                    due_date      = due_date,
                    total_hrs     = total_hours,
                    random_color  = random_color,
                    is_favorite   = False,
                    created_at    = date,
                    updated_at    = date,
                )
                project_data.save()

                for selected_user_id in selected_user_ids:
                    if selected_user_id:
                        try:
                            user_instance  = user_db.objects.get(
                                id=int(selected_user_id)
                            )
                            project_data.users.add(user_instance)
                        except user_db.DoesNotExist:
                            print(f"User with ID {selected_user_id} does not exist.")

                messages.success(request, "Successfully added")
                return redirect("dashboard")
            
            except Exception as e:
                print("Error:", e)
                messages.error(request, "An error occurred while adding the project.")
                return redirect("dashboard")
            
        else:
            return render(request, "index.html")
    else:
        return render(request, "login.html")


def get_project_data(request):
    if request.method  == "GET":
        project_id     = request.GET.get("project_id")
        try:
            project          = project_db.objects.get(id=project_id)
            start_date_obj   = datetime.strptime(project.start_date, "%Y-%m-%d")
            due_date_obj     = datetime.strptime(project.due_date, "%Y-%m-%d")

            selected_users   = project.users.all()  

            selected_user_data = [
                  { 
                      
                    "id": user.id, "name": user.name

                  }   
                 for user in selected_users

            ]

            project_data =  {

                                 "title"          : project.title,
                                 "total_hours"    : project.total_hrs,
                                 "start_date"     : start_date_obj.strftime("%Y-%m-%d"),
                                 "due_date"       : due_date_obj.strftime("%Y-%m-%d"),
                                 "selected_users" : selected_user_data,
      
                            }
            return JsonResponse(project_data)
        except project_db.DoesNotExist:

            return JsonResponse({"error": "Project not found"}, status=404)


def toggle_favorite(request):
    if request.method   == "POST":
        project_id      = request.POST.get("project_id")
        is_favorite     = request.POST.get("is_favorite")
        project         = get_object_or_404(project_db, pk=project_id)

        if is_favorite in ("true", "false"):
            is_favorite         = is_favorite    == "true" 
            project.is_favorite = is_favorite
            project.save()
            return JsonResponse (
                {

                "success": True

                }
                                )
        else:
            return JsonResponse (
                {
                    "success" : False,
                    "error"   : "Invalid is_favorite value"
                }
                                )

    return JsonResponse (
              {
                  
                 "success"  : False, 
                 "error"    : "Invalid request method"

              }
                        )


def update_project(request):
    if request.method == "POST":
        project_id         = request.POST.get("project_id")
        try:
            project             = project_db.objects.get(id=project_id)
            project.title       = request.POST.get("title")
            project.total_hrs   = request.POST.get("total_hours")
            project.start_date  = request.POST.get("start_date")
            project.due_date    = request.POST.get("due_date")

            selected_users      = request.POST.getlist("selected_users")
            project.users.set (selected_users)
            project.is_favorite  = False
            project.save()  
            messages.success(request, "Successfully update")
            return redirect("dashboard")
        
        except project_db.DoesNotExist:
            messages.success(request, "No Project Found")
            return render(request, "index.html")


def deleteProject(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method    == "POST":
            project_id       = request.POST.get("p_id")
            if project_id:
                try:
                    project  = project_db.objects.get(id=project_id)
                    project.delete()

                    messages.success(request, "Successfully Deleted.")

                except project_db.DoesNotExist:
                    messages.error(request, "Project not found.")
            else:
                messages.error(request, "Invalid project ID.")

            return redirect("dashboard")
    else:
        return render(request, "login.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def addTimesheet(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method    == "POST":
            user_id          = request.POST.get("user_id")
            project_id       = request.POST.get("project_id")
            worked_time_str  = request.POST.get("worked_time")
            start_date       = request.POST.get("start_date")
            date             = datetime.now()

            if not re.match(r"^\d+h:\d+m$", worked_time_str):
                messages.error (

                                request,
                                "Invalid worked_time format. Please use the format 'Xh:Ym'."

                               )
                return JsonResponse (

                        {
                           
                        "status": "error"

                        }
                                    )

            worked_time_parts     = worked_time_str.split(":")
            hours                 = int(worked_time_parts[0].strip("h"))
            minutes               = int(worked_time_parts[1].strip("m"))

            total_minutes_worked  = hours * 60 + minutes

            # if total_minutes_worked > 1440:
            #     messages.error (

            #         request, "Worked time should not exceed 24 hours (1440 minutes)."

            #                    )
            #     return JsonResponse (

            #                {
                               
            #                 "status": "error"

            #                 }

            #                         )

            timesheet_data = timesheet_db(
                user_id      = user_id,
                project_id   = project_id,
                worked_time  = worked_time_str,
                date         = start_date,
                created_at   = date,
                updated_at   = date,
            )
            timesheet_data.save()

            return JsonResponse (

                              {
                                  "status": "success"
                              }

                                )
        else:
            user_data       = user_db.objects.all()
            project_data    = project_db.objects.all()
            timesheet_data  = timesheet_db.objects.all()
            context = {

                       "user_data"      : user_data,
                       "project_data"   : project_data,
                       "timesheet_data" : timesheet_data
            
                       }
            
            return render(request, "timesheet.html", context)
    else:
        return render(request, "login.html")


def get_project_title(project_id):
    if project_id is None or project_id == "":
        return "All Projects" 
    
    try:
        project = project_db.objects.get(id=project_id)
        return project.title 
    
    except project_db.DoesNotExist:
        return "Unknown Project"

def get_user_name(user_id):
    if user_id is None or user_id == "":
        return "All Users"
    
    try:
        user = user_db.objects.get(id=user_id)
        return f"{user.name}" 
    except user_db.DoesNotExist:
        return "Unknown User"



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def timesheet_view(request):
    if "adminId" in request.session or "managerId" in request.session:
        selected_user_id         = request.GET.get("user", None)
        selected_project_id      = request.GET.get("project", None)
        selected_start_date      = request.GET.get("start_date", None)
        selected_end_date        = request.GET.get("end_date", None)

        unique_user_ids          = set()

        timesheet_data = timesheet_db.objects.all().order_by("-date", "-created_at")

        project_data             = project_db.objects.all()
        user_data                = user_db.objects.all()

        items_per_page           = 50
        

        for project in project_data:
            for user in project.users.all():
                unique_user_ids.add(user.id)

        unique_users = user_db.objects.filter(id__in=unique_user_ids)

        # Filter timesheet data based on selected user and project
        if selected_project_id and selected_project_id != "All":
            timesheet_data = timesheet_data.filter(project__id=selected_project_id)

            # If a user is selected, further filter by user
            if selected_user_id and selected_user_id != "All":
                timesheet_data = timesheet_data.filter(user__id=selected_user_id)

        elif selected_user_id and selected_user_id != "All":
            timesheet_data = timesheet_data.filter(user__id=selected_user_id)

        if selected_start_date:
            selected_start_date = datetime.strptime(selected_start_date, "%Y-%m-%d").date()
            timesheet_data = timesheet_data.filter(date__gte=selected_start_date)

        if selected_end_date:
            selected_end_date = datetime.strptime(selected_end_date, "%Y-%m-%d").date()
            timesheet_data = timesheet_data.filter(date__lte=selected_end_date)

        total_worked_time        = timedelta()

        for entry in timesheet_data:
            parts         = entry.worked_time.split(":")
            if len(parts) == 2:
                hours               = int(parts[0].rstrip("h")) 
                minutes             = int(parts[1].rstrip("m")) 
                entry_worked_time   = timedelta(hours=hours, minutes=minutes)
                total_worked_time   += entry_worked_time

    
        total_worked_hours          = int(total_worked_time.total_seconds() // 3600)
        total_worked_minutes        = int((total_worked_time.total_seconds() % 3600) // 60)


        total_worked_time_str       = f"{total_worked_hours}h:{total_worked_minutes}m"

        filter_details = {

                             "selected_project_title"  : get_project_title(selected_project_id),
                             "selected_user"           : get_user_name(selected_user_id),
                             "selected_start_date"     : selected_start_date,
                             "selected_end_date"       : selected_end_date

                         }

        total_worked_time_str = f"{total_worked_hours}h:{total_worked_minutes}m"

        # pagination
        paginator = Paginator(timesheet_data, items_per_page)
        page_number = request.GET.get('page', 1)
        
        try:
            # Get the Page object for the current page
            timesheet_page = paginator.page(page_number)
        except PageNotAnInteger:
            # If the page parameter is not an integer, set it to the first page
            timesheet_page = paginator.page(1)
        except EmptyPage:
            # If the page parameter is out of range, deliver the last page
            timesheet_page = paginator.page(paginator.num_pages)

        context = {

            "timesheet_data"     : timesheet_page,
            "project_data"       : project_data,
            "user_data"          : user_data,
            "unique_users"       : unique_users,
            "filter_details"     : filter_details,
            "total_worked_time"  : total_worked_time_str
        }

        return render(request, "timesheet.html", context)
    else:
        return render(request, "login.html")




def get_users_for_project(request, project_id):
    project     = project_db.objects.get(id=project_id)
    users       = project.users.all()

    user_data   = [

                   {
                       
                       "id": user.id, "name": user.name

                   } 
                     for user in users
                  ]

    return JsonResponse(

                    {

                        "users": user_data

                    }

                       )


def validate_worked_time_format(worked_time):
    pattern = r"^\d+h:\d+m$"

    if re.match(pattern, worked_time):
        return True
    
    else:
        return False


def editTimesheet(request, timesheet_id):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method     == "POST":
            try:
                worked_time   = request.POST.get("worked_time")
                start_date    = request.POST.get("start_date")

                if not re.match(r"^\d+h:\d+m$", worked_time):

                    messages.error 
                    (
                        request, "Invalid worked_time format. Use Xh:Ym format."
                    )
                    return JsonResponse (

                        {
                            "status": "error"
                        }

                                         ) 

            
                worked_time_parts     = worked_time.split(":")
                hours                 = int(worked_time_parts[0].strip("h"))
                minutes               = int(worked_time_parts[1].strip("m"))

               
                total_minutes_worked  = hours * 60 + minutes

                # if total_minutes_worked > 1440:
                #     messages.error
                #     (

                #         request,
                #         "Worked time should not exceed 24 hours (1440 minutes)."

                #     )
                #     return JsonResponse (

                #         {
                #             "status": "error"
                #         }

                #                         )

                timesheet_entry              = timesheet_db.objects.get(id=timesheet_id)
                timesheet_entry.worked_time  = worked_time
                timesheet_entry.date         = start_date
                timesheet_entry.save()


                messages.success(request, "Timesheet entry saved successfully")
                return redirect("timesheet")
            
            except timesheet_db.DoesNotExist:
              
                messages.error(request, "Timesheet entry not found.")
            except Exception as e:
     
                messages.error(request, f"Error while saving timesheet entry: {str(e)}")

    return render(request, "timesheet.html")


def deleteTimesheet(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method    == "POST":
            timesheet_id     = request.POST.get("id")
            timesheet_data   = get_object_or_404(timesheet_db, id=timesheet_id)

            timesheet_data.delete()
            messages.success(request, "Successfully Deleted.")

            return redirect("timesheet")
        else:
            return render(request, "timesheet.html")
    else:
        return render(request, "login.html")


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Allotment(request, project_id):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method == "POST":
            date           = datetime.now()
            project_data   = project_db.objects.get(id=project_id)

            allotment = allotment_db (

                           project     = project_data,
                           created_at  = date,
                           updated_at  = date

                                     )
            allotment.save()

            selected_users = []
            hours = []

            for key, value in request.POST.items():
                if key.startswith("selected_user_"):
                    try:
                        user_id = int(value)
                        selected_users.append(user_id)
                    except ValueError:
                        print(f"Illegal value for user_id: {value}")

                elif key.startswith("hours_"):
                    user_hours = value
                    hours.append(user_hours)
            for user_id, user_hour in zip(selected_users, hours):
                if user_id and user_hour:
                    user                     = user_db.objects.get(id=user_id)
                    allotment_user, created  = allotment_user_db.objects.get_or_create(
                        user=user,
                        allotment=allotment,
                        defaults= {

                                     "user_time": user_hour,
                                     "created_at": date,
                                     "updated_at": date

                                   },
                    )
                    if not created:
                        allotment_user.user_time    = user_hour
                        allotment_user.updated_at   = date
                        allotment_user.save()

            return redirect("allotment", project_id=project_id)

        users            = user_db.objects.all()
        project_data     = project_db.objects.get(id=project_id)

        allotment_users  = allotment_user_db.objects.filter(
            allotment__project=project_data
        ).order_by("-created_at")

        users_associated_with_project  = project_data.users.all()

        user_info_list                 = []

        for user in users_associated_with_project:
            user_info   = {

                          "id"    : user.id,
                          "name"  : user.name

                           }
            user_info_list.append(user_info)

        status_value     = None

        for allotment_user_instance in allotment_users:
            related_allotment  = allotment_user_instance.allotment

            # if related_allotment is not None:
            #     status_value   = related_allotment.status

            #     print("Status Value for Allotment User:", status_value)
            # else:
            #     print("Related Allotment is None for Allotment User")

        total_hours      = 0

        for allotment_user in allotment_users:
            user_time_str    = allotment_user.user_time.strip()
            if user_time_str and user_time_str.isdigit():
                total_hours  += int(user_time_str)

        formatted_created_at  = ""
        for allotment_user in allotment_users:
            created_at_str     = allotment_user.created_at

            if created_at_str:
                try:
                    created_at  = datetime.strptime(
                        created_at_str, "%Y-%m-%d %H:%M:%S.%f"
                    )
                    formatted_created_at  = created_at.strftime("%d %b %Y")
                    print(formatted_created_at)
                except ValueError as e:
                    print(f"Error parsing datetime: {e}")
            else:
                print("Empty created_at_str, skipping parsing")

        allotment_json        = json.dumps(
            list(allotment_db.objects.filter(project=project_data).values()),
            default=str,
                                          )
        allotment_users_json  = json.dumps(list(allotment_users.values()), default=str)

        user_info_json        = json.dumps(
            list(users_associated_with_project.values()), default=str
                                          )

        context =  {

                     "user_data"         : users,
                     "project_data"      : project_data,
                     "allotments"        : allotment_json,
                     "allotment_users"   : allotment_users_json,
                     "total_hours"       : total_hours,
                     "req_date"          : formatted_created_at,
                     "status_value"      : status_value,
                     "user_info"         : user_info_list,
                     "user_info_json"    : user_info_json,
                     "navbar"            : "allotment"

                    }

        return render(request, "allotment.html", context)
    else:
        return render(request, "login.html")



@csrf_exempt
def update_allotment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        allotment_id = data.get("allotment_id")
        new_status = data.get("new_status")
        user_data = data.get("user_data")

        try:
            for item in user_data:
                user_id = item.get("userId")
                field = item.get("field")
                new_value = item.get("newValue")
                selected_user = item.get("userSelected")

                # Use filter instead of get to handle the case where multiple objects are returned
                users = allotment_user_db.objects.filter(
                    user_id=user_id,
                    allotment_id=allotment_id
                )

                for user in users:
                    if field == "user_time" and request.session.get("managerId") is not None:
                        user.user_time = new_value

                    if field == "user_alloted":
                        user.user_alloted = new_value

                    if selected_user is not None:
                        selected_user_obj = user_db.objects.get(id=selected_user)
                        user.user = selected_user_obj

                    user.save()

            if new_status and request.session.get("adminId") is not None:
                allotment = allotment_db.objects.get(id=allotment_id)
                allotment.status = new_status
                allotment.save()

            response_data = {
                "success": True
            }

            return JsonResponse(response_data)

        except Exception as e:
            if "Permission denied" not in str(e):
                print(f"Error: {e}")

            response_data = {
                "error": str(e)
            }

            return JsonResponse(response_data, status=400)

    response_data = {"error": "Invalid request method"}
    return JsonResponse(response_data, status=405)








def delete_allotment(request, allotment_id):
    try:
        allotment  = allotment_db.objects.get(id=allotment_id)
        allotment.delete()

        return JsonResponse (
            {

                "success": True

            }     
                            )
    except allotment_db.DoesNotExist:
        return JsonResponse (
            {

            "success": False, 
            "error": "Allotment not found"

            }  
                            )



def delete_allotment_user(request, allotment_id, user_id):
    try:
        # Ensure that the request method is POST
        if request.method == "POST":
            # Find the allotment_user_db instance to delete
            allotment_user = allotment_user_db.objects.get(allotment_id=allotment_id, user_id=user_id)

            # Perform the deletion
            allotment_user.delete()

            # Return success response
            return JsonResponse({"success": True})

    except allotment_user_db.DoesNotExist:
        # Return error response if the allotment_user is not found
        return JsonResponse({"success": False, "error": "Allotment user not found"}, status=404)

    except Exception as e:
        # Return error response for other exceptions
        return JsonResponse({"success": False, "error": str(e)}, status=400)

def milestones(request, project_id):
    if "adminId" in request.session or "managerId" in request.session:
        project_data       = project_db.objects.get(id=project_id)

        if request.method == "POST":
            title            = request.POST["name"]
            release_date     = request.POST["releaseDate"]
            expected_date    = request.POST["expectedCompletionDate"]
            actual_date      = request.POST["actualCompletionDate"]
            completed_tasks  = int(request.POST["completedTasks"])  
            total_tasks      = int(request.POST["totalTasks"]) 

            milestone_data = milestone_db(
                project          = project_data,
                title            = title,
                release_date     = release_date,
                expected_date    = expected_date,
                actual_date      = actual_date,
                completed_tasks  = completed_tasks,
                total_tasks      = total_tasks
            )
            milestone_data.save()

            return redirect (

                           "milestone", 
                            project_id=project_id

                            )

        milestones = milestone_db.objects.filter(project=project_data).order_by(
            "-created_at"
        )

        context =  {

                     "project_data"  : project_data,
                     "milestones"    : milestones,
                     "navbar"        : "milestones"

                   }

    
        for milestone in milestones:
            completed_tasks  = milestone.completed_tasks or 0
            total_tasks      = milestone.total_tasks or 0
            if total_tasks  != 0:
                percentage   = (completed_tasks / total_tasks) * 100
                milestone.completion_percentage  = round(percentage, 2)
            else:
                milestone.completion_percentage  = 0

        return render (

                       request, 
                      "milestones.html", 
                       context

                       )
    else:
        return render(request, "login.html")


def fetch_milestone_data(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method == "GET":
            milestone_id   = request.GET.get("milestone_id")

            try:

                milestone  = milestone_db.objects.get(id=milestone_id)

                milestone_data = {

                                     "id"                        : milestone.id,
                                     "title"                     : milestone.title,
                                     "releaseDate"               : milestone.release_date,
                                     "expectedCompletionDate"    : milestone.expected_date,
                                     "actualCompletionDate"      : milestone.actual_date,
                                     "completedTasks"            : milestone.completed_tasks,
                                     "totalTasks"                : milestone.total_tasks

                                 }

                return JsonResponse(milestone_data)
            except milestone_db.DoesNotExist:
                return JsonResponse({"error": "Milestone not found"}, status=404)

    else:
        return render(request, "login.html")


@csrf_exempt  
def update_milestone(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method    == "POST":
            milestone_id               = request.POST.get("milestone_id")
            new_name                   = request.POST.get("edit_name")
            new_releaseDate            = request.POST.get("edit_releaseDate")
            new_expectedDate           = request.POST.get("edit_expectedCompletionDate")
            new_actualCompletionDate   = request.POST.get("edit_actualCompletionDate")
            new_completedTasks         = request.POST.get("edit_completedTasks")
            new_totalTasks             = request.POST.get("edit_totalTasks")
            try:
                milestone  = milestone_db.objects.get(id=milestone_id)
                milestone.title             = new_name
                milestone.release_date      = new_releaseDate
                milestone.actual_date       = new_actualCompletionDate
                milestone.completed_tasks   = new_completedTasks
                milestone.expected_date     = new_expectedDate
                milestone.total_tasks       = new_totalTasks
                milestone.save()
                success_message             = "Milestone updated successfully"

            except milestone_db.DoesNotExist:
                error_message               = "Milestone not found"

            if success_message:
                return redirect (

                                f'{request.META["HTTP_REFERER"]}?success_message={success_message}'

                                )
            elif error_message:
                return redirect ( 

                                 f'{request.META["HTTP_REFERER"]}?error_message={error_message}'
                               
                                )

        else:
            return render(request, "login.html")


def delete_milestone(request):
    if "adminId" in request.session or "managerId" in request.session:
        if request.method   == "POST":
            milestone_id    = request.POST.get("id")
            project_id      = request.POST.get("project_id")

            try:
                milestone   = get_object_or_404(milestone_db, id=milestone_id)

                if milestone.project.id  == int(project_id):

                    milestone.delete()

                    messages.success (

                                      request,
                                      "Milestone deleted successfully."

                                     )
                    
                    return redirect (

                                      "milestone",
                                       project_id=project_id

                                     )
                else:
                    messages.error (

                                    request, 
                                    "Milestone does not belong to the specified project."

                                    )
                    
            except milestone_db.DoesNotExist:
                messages.error (

                                 request, 
                                 "Milestone not found."
                                 
                                )

        return redirect (

                        "milestone",
                         project_id=project_id
                         
                        )
    else:
        return render(request, "login.html")


def convert_time_to_minutes(time_str):
    if not time_str:
        return 0 
    parts     = time_str.split(":")
    hours     = 0
    minutes   = 0
 
    if len(parts)  > 0:
        if "h" in parts[0]:
            hours   = int(parts[0].rstrip("h"))
        else:
            hours   = int(parts[0])

    if len(parts)  > 1:
        if "m" in parts[1]:
            minutes  = int(parts[1].rstrip("m"))
        else:
            minutes  = int(parts[1])

    total_minutes    = (hours * 60) + minutes

    return total_minutes


def mainLayouts(request, project_id):
    if "adminId" in request.session or "managerId" in request.session:
        project_data       = project_db.objects.get(id=project_id)
        time_sheet_data    = timesheet_db.objects.filter(project=project_data)

        user_worked_time   = {}
        worked_time_hours  = 0
        user_time_hours    = 0

        for entry in time_sheet_data:
            user                 = entry.user.id
            worked_time_str      = entry.worked_time
            worked_time_minutes  = convert_time_to_minutes(worked_time_str)
            worked_time_hours    = worked_time_minutes / 60

            user_worked_time.setdefault(user, 0)
            user_worked_time[user]  += worked_time_hours

        allotment_entries        = allotment_db.objects.filter(project=project_data)
        user_time_dict           = defaultdict(int)

        if allotment_entries.exists():
            approved_allotments   = allotment_entries.filter(status="APPROVED")

            for approved_allotment in approved_allotments:
                allotment_users   = allotment_user_db.objects.filter(
                    allotment=approved_allotment
                )

                for allotment_user in allotment_users:
                    user               = allotment_user.user.id
                    user_time_str      = allotment_user.user_alloted
                    user_time_minutes  = convert_time_to_minutes(user_time_str)

                    user_time_hours    = user_time_minutes / 60

                    user_time_dict[user] += user_time_hours

            total_allotted_time   = sum(user_time_dict.values())

            total_worked_time     = sum(user_worked_time.values())
            consumed_time         = total_worked_time
            total_remaining_time  = total_allotted_time - consumed_time

            if total_allotted_time > 0:
                completion_status_percentage = (
                    total_worked_time / total_allotted_time
                ) * 100
            else:
                completion_status_percentage  = 0

            total_allotted_time_percentage    = 100
            project_data.progress             = round(completion_status_percentage, 2)
            project_data.is_favorite          = False
            project_data.save()

            user_time_list = [
                {
                    "user_id"             : user,
                    "profile_image"       : user_db.objects.get(id=user).profile_image,
                    "position"            : user_db.objects.get(id=user).position,
                    "user_name"           : user_db.objects.get(id=user).name[:12],
                    "difference_hours"    : round (
                        (user_time_dict[user] - user_worked_time.get(user, 0)), 2
                                                  ),
                }
                for user in user_time_dict
            ]
            user_time_list       = user_time_list[:6]

            user_time_dict_list  = [
                {
                    "id"                    : user,
                    "user_name"             : user_db.objects.get(id=user).name,
                    "total_allotted_hours"  : round(user_time_dict[user], 2),
                }
                for user in user_time_dict

                                    ]

            labels = [

                f"{user_info['user_name']} ({round(user_worked_time.get(user_info['id'], 0), 2)} / {round(user_time_dict[user_info['id']], 2)})"
                for user_info in user_time_dict_list

                     ]

            data = {
                "labels"    : labels,
                "datasets"  : [
                    {
                        "label"  : "Time Worked Percentage",
                        "data"   : [
                            round(
                                (
                                    user_worked_time.get(user_info["id"], 0)
                                    / user_time_dict[user_info["id"]]
                                )
                                * 100,
                                2,
                            )
                            if user_time_dict[user_info["id"]] != 0
                            else 0
                            for user_info in user_time_dict_list
                        ],
                        "backgroundColor" : "rgb(248 87 110)",
                        "borderColor"     : "rgb(248 87 110)",
                        "borderWidth"     : 1,
                    }
                ],
            }

            context = {

                          "project_data"                          : project_data,
                          "navbar"                                : "dashboard",
                          "worked_time_hours"                     : worked_time_hours,
                          "user_time_hours"                       : user_time_hours,
                          "user_time_list"                        : user_time_list,
                          "total_allotted_time"                   : total_allotted_time,
                          "total_allotted_time_percentage"        : total_allotted_time_percentage,
                          "total_worked_time"                     : round(total_worked_time, 2),
                          "consumed_time"                         : round(consumed_time, 2),
                          "total_remaining_time"                  : round(total_remaining_time, 2),
                          "completion_status_percentage"          : round(completion_status_percentage, 2),
                          "completion_status_percentage_rounded"  : round(completion_status_percentage),
                          "user_time_dict"                        : user_time_dict_list,
                          "chart_data"                            : data,
                
                      }

        else:
            messages.error(
                request, "There are no approved allotments for this project."
            )

            context = {
                "project_data"  : project_data,
                "navbar"        : "dashboard",
            }

        return render(request, "project-dashboard.html", context)
    else:
        return render(request, "login.html")



def format_minutes_as_time(minutes):
    # Convert total minutes to hours and minutes
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h:{int(minutes)}m"


def userListWorkBook(request):
    users = user_db.objects.all().order_by('name')

    # Set the first user as the default user
    default_user = users.first()

    projects = project_db.objects.filter(users=default_user)
    project_details = []
    total_remaining_minutes = 0  # Track total remaining minutes for the user

    for project in projects:
        approved_allotments = allotment_db.objects.filter(project=project, status="APPROVED")
        user_alloted_sum = 0
        worked_time_sum_minutes = 0

        timesheet_entries = set()
        allotment_user_entries = set()

        for approved_allotment in approved_allotments:
            timesheets = timesheet_db.objects.filter(user=default_user, project=project)
            allotment_users = allotment_user_db.objects.filter(allotment=approved_allotment, user=default_user)

            for timesheet in timesheets:
                if timesheet.id not in timesheet_entries:
                    worked_time_sum_minutes += convert_time_to_minutes(timesheet.worked_time)
                    timesheet_entries.add(timesheet.id)

            for allotment_user in allotment_users:
                if allotment_user.id not in allotment_user_entries:
                    user_alloted_sum += float(allotment_user.user_alloted)
                    allotment_user_entries.add(allotment_user.id)

        # Calculate remaining minutes after subtracting worked time from allotted time
        remaining_minutes = max(0, user_alloted_sum * 60 - worked_time_sum_minutes)

        # Track total remaining minutes for the user across all projects
        total_remaining_minutes += remaining_minutes

        # Calculate hours and minutes for the formatted result
        hours, minutes = divmod(remaining_minutes, 60)

        # Format the subtraction result as "1h:10m"
        formatted_subtraction_result = f"{int(hours)}h:{int(minutes)}m"

        project_details.append({
            'project_title': project.title,
            'user_alloted_sum': int(user_alloted_sum),  # Convert to int to remove decimal
            'worked_time_sum_hours': int(worked_time_sum_minutes // 60),
            'worked_time_sum_minutes': int(worked_time_sum_minutes % 60),
            'formatted_subtraction_result': formatted_subtraction_result
        })

    # Calculate total hours and minutes for the formatted result
    total_hours, total_minutes = divmod(total_remaining_minutes, 60)

    # Format the total remaining result as "1h:10m"
    total_remaining_result = f"{int(total_hours)}h:{int(total_minutes)}m"
   

    context = {
        'users': users,
        'selected_user': default_user,
        'project_details': project_details,
        'total_remaining_result': total_remaining_result
    }

    return render(request, 'workbook.html', context)




def userWorkBook(request, user_id):
    selected_user = get_object_or_404(user_db, id=user_id)

    # Fetch projects for the selected user
    projects = project_db.objects.filter(users=selected_user)

    # List to store dictionaries for each project
    project_details = []
    total_remaining_minutes = 0  # Track total remaining minutes for the user

    for project in projects:
        approved_allotments = allotment_db.objects.filter(project=project, status="APPROVED")
        user_alloted_sum = 0
        worked_time_sum_minutes = 0

        timesheet_entries = set()
        allotment_user_entries = set()

        for approved_allotment in approved_allotments:
            timesheets = timesheet_db.objects.filter(user=selected_user, project=project)
            allotment_users = allotment_user_db.objects.filter(allotment=approved_allotment, user=selected_user)

            for timesheet in timesheets:
                if timesheet.id not in timesheet_entries:
                    worked_time_sum_minutes += convert_time_to_minutes(timesheet.worked_time)
                    timesheet_entries.add(timesheet.id)

            for allotment_user in allotment_users:
                if allotment_user.id not in allotment_user_entries:
                    user_alloted_value = allotment_user.user_alloted.strip() if allotment_user.user_alloted else None

                    if user_alloted_value:
                        try:
                            user_alloted_sum += float(user_alloted_value)
                        except ValueError as e:
                            print(f"Error converting to float: {e}, user_alloted value: {user_alloted_value}")
                    else:
                        print("Warning: Empty or whitespace user_alloted value encountered.")

                    allotment_user_entries.add(allotment_user.id)

        # Calculate remaining minutes after subtracting worked time from allotted time
        remaining_minutes = max(0, user_alloted_sum * 60 - worked_time_sum_minutes)

        # Track total remaining minutes for the user across all projects
        total_remaining_minutes += remaining_minutes

      # Calculate hours and minutes for the formatted result
        hours, minutes = divmod(remaining_minutes, 60)

        # Format the subtraction result without decimal points for hours
        formatted_subtraction_result = f"{int(hours)}h:{int(minutes)}m"



        project_details.append({
            'project_title': project.title,
            'user_alloted_sum': int(user_alloted_sum),  # Convert to int to remove decimal
            'worked_time_sum_hours': int(worked_time_sum_minutes // 60),
            'worked_time_sum_minutes': int(worked_time_sum_minutes % 60),
            'formatted_subtraction_result': formatted_subtraction_result
        })

    # Calculate total hours and minutes for the formatted result
    total_hours, total_minutes = divmod(total_remaining_minutes, 60)

    # Format the total remaining result as "1h:10m"
    total_remaining_result = f"{int(total_hours)}h:{int(total_minutes)}m"

    context = {
        'users': user_db.objects.all().order_by('name'),
        'selected_user': selected_user,
        'project_details': project_details,
        'total_remaining_result': total_remaining_result,
    }

    return render(request, 'workbook.html', context)
