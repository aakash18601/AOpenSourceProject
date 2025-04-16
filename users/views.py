from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model

User = get_user_model()
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Student
from django.contrib.auth.forms import UserChangeForm
import datetime
import random
from .models import Enrollment


# ------------------------- LANDING PAGE -------------------------
def landing_page(request):
    return render(request, "users/landing.html")


# ------------------------- DASHBOARDS -------------------------


# Main Dashboard - Redirects user based on role
@login_required
def dashboard(request):
    if request.user.is_staff and request.path != "/faculty_dashboard/":
        return redirect("faculty_dashboard")
    elif not request.user.is_staff and request.path != "/student_dashboard/":
        return redirect("student_dashboard")
    return HttpResponse("Redirecting...")  # Just for debugging


# Student Dashboard with Progress Tracking
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Enrollment  # Ensure you have imported your model


# Student Dashboard with Progress Tracking
@login_required
def student_dashboard(request):
    """Display the student dashboard with enrolled courses and progress."""
    try:
        student = request.user.student
        enrollments = Enrollment.objects.filter(student=student)
        enrolled_course_ids = enrollments.values_list("course_id", flat=True)
        available_courses = Course.objects.exclude(id__in=enrolled_course_ids)
    except Student.DoesNotExist:
        enrollments = []
        available_courses = Course.objects.all()

    return render(
        request,
        "users/student_dashboard.html",
        {
            "enrollments": enrollments,
            "available_courses": available_courses,
        },
    )


# Faculty Dashboard (Placeholder for now)
@login_required
def faculty_dashboard(request):
    return render(request, "users/faculty_dashboard.html")


# ------------------------- COURSE MANAGEMENT -------------------------


# List all available courses
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, "users/course_list.html", {"courses": courses})


# Enroll a student in a course
@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    try:
        student = request.user.student  # Ensure user is a student
    except Student.DoesNotExist:
        messages.error(request, "Only students can enroll in courses.")
        return redirect("student_dashboard")

    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.warning(request, "You are already enrolled in this course!")
    else:
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, "Successfully enrolled in the course!")

    return redirect("course_list")


# Show enrolled courses for a student
@login_required
def my_courses(request):
    enrolled_courses = Enrollment.objects.filter(student=request.user)

    # Calculate progress for each course
    for enrollment in enrolled_courses:
        enrollment.progress = enrollment.calculate_progress()

    return render(
        request, "users/my_courses.html", {"enrolled_courses": enrolled_courses}
    )


# Unenroll a student from a course
@login_required
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        enrollment = Enrollment.objects.filter(
            student=request.user, course=course
        ).first()
        if enrollment:
            enrollment.delete()
            messages.success(request, f"You have been unenrolled from {course.name}.")
        else:
            messages.error(request, "You are not enrolled in this course.")

        return redirect("my_courses")

    return render(request, "users/confirm_unenroll.html", {"course": course})


# ------------------------- ATTENDANCE -------------------------


def attendance(request):
    # Sample attendance data with MCA subjects
    mca_subjects = [
        "Data Structures & Algorithms",
        "Operating Systems",
        "Database Management Systems",
        "Computer Networks",
        "Software Engineering",
        "Web Technologies",
        "Artificial Intelligence",
        "Machine Learning",
        "Cyber Security",
        "Cloud Computing",
    ]

    # Generating dummy attendance data
    attendance_data = [
        {
            "course": subject,
            "date": datetime.date.today(),
            "status": "Present" if i % 2 == 0 else "Absent",
        }
        for i, subject in enumerate(mca_subjects)
    ]

    return render(
        request, "users/attendance.html", {"attendance_data": attendance_data}
    )


# ------------------------- USER AUTHENTICATION -------------------------


# User Registration
def register_user(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]
        is_faculty = request.POST.get("is_faculty") == "on"

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        # Set role based on checkbox
        role = "faculty" if is_faculty else "student"

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,  # 🔥 important
        )

        # If faculty, set is_staff for Django admin access (optional)
        user.is_staff = is_faculty
        user.save()

        # Create profile based on role
        if role == "student":
            from .models import Student

            Student.objects.create(user=user)
        elif role == "faculty":
            from .models import Faculty

            Faculty.objects.create(user=user)

        messages.success(request, "Registration successful! You can now log in.")
        return redirect("login")

    return render(request, "users/register.html")


# User Login
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Redirect based on user role
            if user.role == "student":
                return redirect("student_dashboard")
            elif user.role == "faculty":
                return redirect("faculty_dashboard")
            elif user.role == "admin":
                return redirect("admin_dashboard")  # If you create one
            else:
                return redirect("dashboard")  # Default

        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "users/login.html")


# User Logout
def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# ------------------------- USER PROFILE MANAGEMENT


# Profile Page
@login_required
def profile(request):
    enrolled_courses = Enrollment.objects.filter(student=request.user)

    # Calculate progress for each enrolled course
    for enrollment in enrolled_courses:
        enrollment.progress = enrollment.calculate_progress()

    return render(request, "users/profile.html", {"enrolled_courses": enrolled_courses})


# Edit Profile
@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("profile")
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, "users/edit_profile.html", {"form": form})


@login_required
@login_required
def enroll_course(request, course_id):
    print(f"▶ Enroll function triggered for course ID: {course_id}")  # Debug

    course = get_object_or_404(Course, id=course_id)
    print(f"✅ Found Course: {course.name}")  # Debug

    try:
        student = request.user.student
        print(f"👤 Student: {student.user.username}")
    except Student.DoesNotExist:
        messages.error(request, "Only students can enroll in courses.")
        return redirect("student_dashboard")

    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
    else:
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, f"Successfully enrolled in {course.name}!")
        print(f"✅ Enrollment created for {student.user.username} in {course.name}")

    return redirect("student_dashboard")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect("faculty_dashboard")
            return redirect("student_dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "users/login.html")


def manage_enrollments(request):
    # Get courses taught by the logged-in faculty
    faculty_courses = Course.objects.filter(instructor=request.user)

    # Get enrolled students for these courses
    enrollments = Enrollment.objects.filter(course__in=faculty_courses)

    context = {"faculty_courses": faculty_courses, "enrollments": enrollments}
    return render(request, "faculty/manage_enrollments.html", context)


def student_list(request):
    students = Student.objects.all()  # Fetch all students
    return render(request, "users/student_list.html", {"students": students})


def course_summary(request):
    student = request.user  # Assuming the user is a student
    enrolled_courses = Enrollment.objects.filter(student=student)

    context = {"enrolled_courses": enrolled_courses}
    return render(request, "users/course_summary.html", context)


@login_required
def manage_courses(request):
    courses = Course.objects.filter(instructor=request.user)
    return render(request, "users/manage_courses.html", {"courses": courses})


@login_required
def review_performance(request):
    user = request.user

    if user.role != "faculty":
        return redirect("faculty_dashboard")

    faculty = user.faculty
    courses = Course.objects.filter(faculty=faculty)
    enrollments = Enrollment.objects.filter(course__in=courses).select_related(
        "student", "course"
    )

    performance_data = []

    for enroll in enrollments:
        student_name = enroll.student.get_full_name()
        course_name = enroll.course.name
        progress = f"{random.randint(60, 100)}%"  # Optional placeholder, replace with enroll.progress if needed

        performance_data.append(
            {
                "student_name": student_name,
                "course": course_name,
                "progress": progress,
            }
        )

    context = {
        "performance_data": performance_data,
    }
    return render(request, "users/review_performance.html", context)


def course_list(request):
    student = request.user.student
    enrolled_course_ids = Enrollment.objects.filter(student=student).values_list(
        "course_id", flat=True
    )
    available_courses = Course.objects.exclude(id__in=enrolled_course_ids)
    return render(
        request,
        "users/available_courses.html",
        {"available_courses": available_courses},
    )
