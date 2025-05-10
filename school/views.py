from datetime import date
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.http import JsonResponse
from .models import Attendance, Notification, Student

# Create your views here.

def index(request):
    return render(request, "authentication/login.html")

def dashboard(request):
    unread_notification = Notification.objects.filter(user=request.user, is_read=False)
    unread_notification_count = unread_notification.count()
    return render(request, "students/student-dashboard.html")

 
def teachers_dashboard(request):
    # Sample data - replace with DB queries later
    unit_count = 3  # it can fetch from a Unit model filtered by teacher

    timetable = [
        {'day': 'Monday', 'time': '9:00 AM - 10:30 AM', 'unit': 'Internet Technologies', 'room': 'SCC106'},
        {'day': 'Wednesday', 'time': '11:00 AM - 12:30 PM', 'unit': 'OOP 1', 'room': 'CLB107'},
        {'day': 'Friday', 'time': '1:00 PM - 2:30 PM', 'unit': 'Internet Application Programming 1', 'room': 'SCC108'},
    ]

    notifications = ['Grade submission deadline is Friday.', 'Staff meeting tomorrow at 3 PM.']
    events = ['Parent-Teacher Conference - May 15', 'Exam Week - Starts May 20']

    return render(request, 'teachers/teacher_dashboard.html', {
        'unit_count': unit_count,
        'timetable': timetable,
        'notifications': notifications,
        'events': events,
    })





def mark_notification_as_read(request):
    if request.method == 'POST':
        notification = Notification.objects.filter(user=request.user, is_read=False)
        notification.update(is_read=True)
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden()

def clear_all_notification(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user)
        notification.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseForbidden

def mark_attendance(request):
    today = date.today()
    students = Student.objects.all()
    summary = None

    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            Attendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={'status': status}
            )

        # Generate summary after submission
        present_count = Attendance.objects.filter(date=today, status='present').count()
        absent_count = Attendance.objects.filter(date=today, status='absent').count()

        summary = {
            'date': today.strftime("%A, %d %B %Y"),  # e.g., Saturday, 10 May 2025
            'present': present_count,
            'absent': absent_count
        }

    return render(request, "teachers/mark_attendance.html", {
        'students': students,
        'summary': summary,
    })

def upload_materials(request):
    return render(request, "teachers/upload_materials.html")

from django.shortcuts import render, redirect
from .forms import AssignmentForm
from .models import Assignment

def create_assignment(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')  # Redirect to dashboard
    else:
        form = AssignmentForm()

    return render(request, 'teachers/create_assignment.html', {'form': form})

def teacher_dashboard(request):
    assignments = Assignment.objects.all().order_by('-created_at')
    return render(request, 'teachers/teacher_dashboard.html', {'assignments': assignments})
