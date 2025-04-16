from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    dashboard,
    landing_page,
    course_list,
    enroll_in_course,
    my_courses,
    unenroll_course,
    register_user,
    login_user,
    logout_user,
    profile,
    edit_profile,
    student_dashboard,
    faculty_dashboard,
    attendance,
    enroll_course,
    manage_enrollments,
    manage_courses,
    student_list,
    course_summary,
)

urlpatterns = [
    # General Pages
    path("", landing_page, name="landing_page"),
    path("dashboard/", dashboard, name="dashboard"),
    # Student Routes
    path("student/courses/", course_list, name="course_list"),
    path("student_dashboard/", student_dashboard, name="student_dashboard"),
    path("student/my-courses/", my_courses, name="my_courses"),
    path("student/unenroll/<int:course_id>/", unenroll_course, name="unenroll_course"),
    path("student/attendance/", attendance, name="attendance"),
    path("student_list/", student_list, name="student_list"),
    path("student/course-summary/", course_summary, name="course_summary"),
    # Faculty Routes
    path("faculty/dashboard/", faculty_dashboard, name="faculty_dashboard"),
    path("faculty/manage-enrollments/", manage_courses, name="manage_enrollments"),
    path("faculty/track-attendance/", attendance, name="track_attendance"),
    path("faculty/review-performance/", dashboard, name="review_performance"),
    path("enroll/<int:course_id>/", enroll_in_course, name="enroll_in_course"),
    # Authentication
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    # Profile Management
    path("profile/", profile, name="profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
