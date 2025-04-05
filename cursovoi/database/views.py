from os import error

from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils.deprecation import MiddlewareMixin

from .models import Students, Teachers, Faculties, Departments, Specialties, Groups, Subjects, Curriculum, Grades
from .forms import UserRegisterForm, StudentsForm, TeachersForm, LoginForm, UserPasswordChangeForm, GradeForm
from django.views.generic import DetailView, UpdateView, DeleteView
from datetime import datetime
from django.db.models import Prefetch


class StudentsDetailView(DetailView):
    model = Students
    template_name = 'database/details_view.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_semester = 1 if current_month < 7 else 2

        total_semesters = (current_year - student.group.year_of_admission) * 2 + current_semester
        course = total_semesters // 2

        context['course'] = course
        return context

class StudentsUpdateView(UpdateView):
    model = Students
    template_name = 'database/students-update.html'
    context_object_name = 'student'
    form_class = StudentsForm

    # Проверка доступа: пользователь может редактировать только свой профиль или быть администратором
    def test_func(self):
        student = self.get_object()
        return self.request.user.is_superuser or self.request.user == student.user_id

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            # Ограничиваем поля для обычного пользователя
            form.fields.pop('last_name')
            form.fields.pop('first_name')
            form.fields.pop('father_name')
            form.fields.pop('birth_date')
            form.fields.pop('gender')
            form.fields.pop('group')
        return form


class StudentsDeleteView(DeleteView):
    model = Students
    success_url = '/database/'
    template_name = 'database/students-delete.html'
    context_object_name = 'student'

class StudentSubjectsView(DetailView):
    model = Students
    template_name = 'database/student_subjects.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        subjects = Subjects.objects.prefetch_related(
            Prefetch('curriculum_set', queryset=Curriculum.objects.filter(group_number=student.group))
        ).filter(curriculum__group_number=student.group).order_by('name')

        context['subjects'] = subjects
        return context


class StudentGradesView(DetailView):
    model = Students
    template_name = 'database/student_grades.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object

        # Оптимизированный запрос с select_related
        curriculum = Curriculum.objects.filter(
            group_number=student.group
        ).select_related('subject_id', 'teacher_id')

        # Получаем все оценки студента одним запросом
        grades = Grades.objects.filter(
            student_id=student
        ).select_related('subject_id')

        # Создаем словарь для быстрого доступа к оценкам
        grades_dict = {
            grade.subject_id.id: grade
            for grade in grades
        }

        # Формируем структуру данных для шаблона
        subjects_with_grades = [
            {
                'subject': entry.subject_id,
                'semester': entry.semester,
                'grade': grades_dict.get(entry.subject_id.id)
            }
            for entry in curriculum
        ]

        # Сортируем сначала по семестру, затем по названию предмета
        subjects_with_grades.sort(key=lambda x: (x['semester'], x['subject'].name.lower()))

        context['subjects_with_grades'] = subjects_with_grades

        return context



# --- teacher --- teacher --- teacher --- #


class TeachersDetailView(DetailView):
    model = Teachers
    template_name = 'database/details_view2.html'
    context_object_name = 'teacher'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все предметы, связанные с преподавателем через Curriculum
        context['teacher_subjects'] = Subjects.objects.filter(curriculum__teacher_id=self.object).distinct()
        return context

class TeachersUpdateView(UpdateView):
    model = Teachers
    template_name = 'database/teachers-update.html'
    form_class = TeachersForm
    context_object_name = 'teacher'

    # Проверка доступа: пользователь может редактировать только свой профиль или быть администратором
    def test_func(self):
        teacher = self.get_object()
        return self.request.user.is_superuser or self.request.user == teacher.user_id

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_superuser:
            # Ограничиваем поля для обычного пользователя
            form.fields.pop('last_name')
            form.fields.pop('first_name')
            form.fields.pop('father_name')
            form.fields.pop('birth_date')
            form.fields.pop('gender')
            form.fields.pop('department_name')
            form.fields.pop('post')

        return form


class TeachersDeleteView(DeleteView):
    model = Teachers
    success_url = '/database/database2'
    template_name = 'database/teachers-delete.html'
    context_object_name = 'teacher'


def faculty_department_teacher_view(request):
    faculties = Faculties.objects.prefetch_related('departments__teachers')
    return render(request, 'database/faculty_department_teacher.html', {'faculties': faculties})


def faculties_list(request):
    faculties = Faculties.objects.all()
    return render(request, 'database/faculties.html', {'faculties': faculties})


def faculties_detail(request, pk):
    faculty = get_object_or_404(Faculties, id=pk)
    departments = Departments.objects.filter(faculty_name=faculty)
    specialties = Specialties.objects.filter(department_name__in=departments)
    groups = Groups.objects.filter(specialty_name__in=specialties)

    # Расчёт курсов
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_semester = 1 if current_month < 7 else 2

    courses = {}
    for group in groups:
        course = ((current_year - group.year_of_admission) * 2 + current_semester) // 2

        if group.specialty_name.period_of_study == "3 года 10 месяцев" and course > 4:
            continue

        if course not in courses:
            courses[course] = []
        courses[course].append(group)

    return render(request, 'database/faculties_detail.html', {
        'faculty': faculty,
        'courses': courses  # Передаём курсы вместо групп
    })

def group_detail(request, pk):
    group = get_object_or_404(Groups, id=pk)
    students = Students.objects.filter(group=group)
    return render(request, 'database/group_detail.html', {
        'group': group,
        'students': students
    })

# ФОРМА ДОБАВЛЕНИЯ СТУДЕНТОВ

def create(request):
    referer = request.META.get('HTTP_REFERER', '/')

    if request.user.is_authenticated:
        if hasattr(request.user, 'students'):
            if request.user.students.role == 'Студент':
                return render(request, 'database/access_rights.html', {'referer': referer})
        elif hasattr(request.user, 'teachers'):
            if request.user.teachers.role == 'Преподаватель':
                return render(request, 'database/access_rights.html', {'referer': referer})
        elif request.user.is_superuser:
            pass
        else:
            return render(request, 'database/access_rights.html', {'referer': referer})

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        form = StudentsForm(request.POST, request.FILES)

        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            student = form.save(commit=False)
            student.user_id = user
            student.save()
            #login(request, user)
            return redirect('create')
        else:
            # Если формы невалидны, вернём их с ошибками
            return render(request, 'database/create.html', {
                'user_form': user_form,
                'form': form
            })
    else:
        user_form = UserRegisterForm()
        form = StudentsForm()

        return render(request, 'database/create.html', {
            'user_form': user_form,
            'form': form
        })


# ФОРМА ДОБАВЛЕНИЯ ПРЕПОДАВАТЕЛЕЙ

def create2(request):
    referer = request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated:
        if hasattr(request.user, 'students'):
            if request.user.students.role == 'Студент':
                return render(request, 'database/access_rights.html', {'referer': referer})
        elif hasattr(request.user, 'teachers'):
            if request.user.teachers.role == 'Преподаватель':
                return render(request, 'database/access_rights.html', {'referer': referer})
        elif request.user.is_superuser:
            pass
        else:
            return render(request, 'database/access_rights.html', {'referer': referer})

    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        form = TeachersForm(request.POST, request.FILES)

        if user_form.is_valid() and form.is_valid():
            user = user_form.save()
            teacher = form.save(commit=False)
            teacher.user_id = user
            teacher.save()
            #login(request, user)
            return redirect('create2')
        else:
            # Если формы невалидны, вернём их с ошибками
            return render(request, 'database/create.html', {
                'user_form': user_form,
                'form': form
            })
    else:
        user_form = UserRegisterForm()
        form = TeachersForm()

        return render(request, 'database/create2.html', {
            'user_form': user_form,
            'form': form
        })


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'students'):
                    return redirect('students-detail', pk=user.students.pk)
                elif hasattr(user, 'teachers'):
                    return redirect('teachers-detail', pk=user.teachers.pk)
                else: return redirect('faculties-list')
    else:
        form = LoginForm()
    return render(request, 'database/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def password_change(request):
    if request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            if hasattr(user, 'students'):
                return redirect('students-detail', pk=user.students.pk)
            elif hasattr(user, 'teachers'):
                return redirect('teachers-detail', pk=user.teachers.pk)
            else:
                return redirect('home')
    else:
        form = UserPasswordChangeForm(request.user)

    referer = request.META.get('HTTP_REFERER', '/')

    return render(request, 'database/password_change.html', {'form': form, 'referer': referer})

@login_required
def grade_management(request):
    teacher = request.user.teachers
    subjects = Subjects.objects.filter(curriculum__teacher_id=teacher).distinct()

    selected_subject = None
    selected_group = None
    formset = None
    groups = Groups.objects.none()

    # GET-запрос (выбор предмета/группы)
    if request.method == 'GET':
        # Получаем выбранные предмет и группу из GET-параметров
        selected_subject_id = request.GET.get('subject')
        selected_group_id = request.GET.get('group')

        if selected_subject_id:
            selected_subject = get_object_or_404(Subjects, pk=selected_subject_id)
            groups = Groups.objects.filter(
                curriculum__subject_id=selected_subject,
                curriculum__teacher_id=teacher
            ).distinct()

            if selected_group_id:
                selected_group = get_object_or_404(Groups, pk=selected_group_id)
                students = Students.objects.filter(group=selected_group)

                # Создаем оценки для всех студентов, если их нет
                for student in students:
                    Grades.objects.get_or_create(
                        student_id=student,
                        subject_id=selected_subject
                    )

                # Формируем queryset для всех студентов группы
                GradeFormSet = modelformset_factory(
                    Grades,
                    form=GradeForm,
                    extra=0  # Не создавать пустые формы
                )
                formset = GradeFormSet(
                    queryset=Grades.objects.filter(
                        student_id__in=students,
                        subject_id=selected_subject
                    ),
                    form_kwargs={'assessment_form': selected_subject.assessment_form}
                )

    # POST-запрос (сохранение оценок)
    elif request.method == 'POST':
        selected_subject = get_object_or_404(Subjects, pk=request.POST.get('subject'))
        selected_group = get_object_or_404(Groups, pk=request.POST.get('group'))
        students = Students.objects.filter(group=selected_group)

        groups = Groups.objects.filter(
            curriculum__subject_id=selected_subject,
            curriculum__teacher_id=teacher
        ).distinct()

        GradeFormSet = modelformset_factory(
            Grades,
            form=GradeForm,
            extra=0
        )
        formset = GradeFormSet(
            request.POST,
            queryset=Grades.objects.filter(
                student_id__in=students,
                subject_id=selected_subject
            ),
            form_kwargs={'assessment_form': selected_subject.assessment_form}
        )

        if formset.is_valid():
            formset.save()

    context = {
        'subjects': subjects,
        'groups': groups if selected_subject else Groups.objects.none(),
        'selected_subject': selected_subject,
        'selected_group': selected_group,
        'formset': formset,
    }
    return render(request, 'database/grades.html', context)

def access_rights(request):
    return render(request,'database/access_rights.html')


def redirect_to_personal_page(request):
    user = request.user

    # Проверяем роль пользователя через связанные модели
    if hasattr(user, 'students'):  # Если пользователь — студент
        return redirect('students-detail', pk=user.students.pk)
    elif hasattr(user, 'teachers'):  # Если пользователь — преподаватель
        return redirect('teachers-detail', pk=user.teachers.pk)