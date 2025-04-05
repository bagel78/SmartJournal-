from django.urls import path
from . import views

urlpatterns = [

    path('', views.login_view, name='login'),
    path('access_rights', views.access_rights, name='access'),
    path('redirect/', views.redirect_to_personal_page, name='redirect-to-personal-page'),

    path('create', views.create, name='create'),
    path('create2', views.create2, name='create2'),

    path('<int:pk>', views.StudentsDetailView.as_view(), name='students-detail'),
    path('<int:pk>/update', views.StudentsUpdateView.as_view(), name='students-update'),
    path('<int:pk>/delete', views.StudentsDeleteView.as_view(), name='students-delete'),
    path('<int:pk>/subjects/', views.StudentSubjectsView.as_view(), name='student_subjects'),
    path('<int:pk>/grades/', views.StudentGradesView.as_view(), name='student_grades'),

    path('database2/<int:pk>', views.TeachersDetailView.as_view(), name='teachers-detail'),
    path('database2/<int:pk>/update', views.TeachersUpdateView.as_view(), name='teachers-update'),
    path('database2/<int:pk>/delete', views.TeachersDeleteView.as_view(), name='teachers-delete'),
    path('faculties2/', views.faculty_department_teacher_view, name='faculty_department_teacher'),

    path('faculties', views.faculties_list, name='faculties-list'),
    path('faculties/<int:pk>/', views.faculties_detail, name='faculties-detail'),
    path('groups/<int:pk>/', views.group_detail, name='group-detail'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', views.password_change, name='password_change'),

    path('grades/', views.grade_management, name='grade_management'),

]

