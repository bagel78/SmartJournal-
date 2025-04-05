from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Faculties(models.Model):
    name = models.CharField('Факультет', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'

class Departments(models.Model):
    name = models.CharField('Кафедра', max_length=100)
    faculty_name = models.ForeignKey(Faculties, on_delete=models.CASCADE, related_name='departments', verbose_name='Факультет')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'

class Specialties(models.Model):
    FORM_OF_EDUCATION_CHOICES = [
        ('Очная', 'Очная'),
        ('Заочная', 'Заочная'),
        ('Очно-заочная','Очно-заочная'),
    ]

    PERIOD_OF_STUDY_CHOICES = [
        ('3 года 10 месяцев', '3 года 10 месяцев'),
        ('4 года 10 месяцев', '4 года 10 месяцев'),
    ]

    number = models.CharField('Номер специальности', max_length= 10)
    name = models.CharField('Специальность', max_length=100)
    form_of_education = models.CharField('Форма обучения', max_length=15, choices=FORM_OF_EDUCATION_CHOICES)
    period_of_study = models.CharField('Срок обучения', max_length=50, choices=PERIOD_OF_STUDY_CHOICES)
    department_name = models.ForeignKey(Departments, on_delete=models.CASCADE, verbose_name='Кафедра')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Специальность'
        verbose_name_plural = 'Специальности'

class Groups(models.Model):
    number = models.CharField('Номер группы', max_length=10)
    year_of_admission = models.IntegerField('Год поступления')
    specialty_name = models.ForeignKey(Specialties, on_delete=models.CASCADE, verbose_name='Специальность')

    def __str__(self):
        return self.number

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

class Subjects(models.Model):
    ASSESSMENT_FORM_CHOICES = [
        ('Экзамен', 'Экзамен'),
        ('Зачет', 'Зачет'),
    ]
    name = models.CharField('Название предмета', max_length=100)
    assessment_form = models.CharField('Форма оценивания', max_length=10, choices=ASSESSMENT_FORM_CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

class Students(models.Model):
    GENDER_CHOICES = [
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    ]
    last_name = models.CharField('Фамилия', max_length=50)
    first_name = models.CharField('Имя', max_length=25)
    father_name = models.CharField('Отчество', max_length=50, blank=True)
    birth_date = models.DateField('Дата рождения')
    gender = models.CharField('Пол', max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, verbose_name='Группа')
    role = models.CharField('Роль', max_length=20, default='Студент', editable=False, blank=False, null=False)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True) # Связь с USER
    photo = models.ImageField('Фотография', upload_to='photos', blank=True)

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/database/img/user_photo (1).png'

    def delete(self, *args, **kwargs):
        if self.user_id:
            self.user_id.delete()  # Удаление связанного пользователя
        super().delete(*args, **kwargs)

    def get_grades(self):
        return Grades.objects.filter(student_id=self)

    def __str__(self):
        return self.last_name

    def get_absolute_url(self):
        return reverse('students-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

class Teachers(models.Model):
    GENDER_CHOICES = [
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    ]
    POST_CHOICES = [
        ('Ассистент', 'Ассистент'),
        ('Преподаватель', 'Преподаватель'),
        ('Старший преподаватель', 'Старший преподаватель'),
        ('Доцент', 'Доцент'),
        ('Профессор', 'Профессор'),
        ('Заведующий кафедрой', 'Заведующий кафедрой'),
        ('Декан', 'Декан'),
    ]
    last_name = models.CharField('Фамилия', max_length=50)
    first_name = models.CharField('Имя', max_length=25)
    father_name = models.CharField('Отчество', max_length=50, blank=True)
    birth_date = models.DateField('Дата рождения')
    gender = models.CharField('Пол', max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    department_name = models.ForeignKey(Departments, on_delete=models.CASCADE, related_name='teachers', verbose_name='Кафедра')
    post = models.CharField('Должность', max_length=30, choices=POST_CHOICES)
    role = models.CharField('Роль', max_length=20, default='Преподаватель', editable=False, blank=False, null=False)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, null=True) # Связь с USER
    photo = models.ImageField('Фотография', upload_to='photos', blank=True)

    def get_photo_url(self):
        if self.photo:
            return self.photo.url
        return '/static/database/img/user_photo (1).png'

    def delete(self, *args, **kwargs):
        if self.user_id:
            self.user_id.delete()  # Удаление связанного пользователя
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.last_name

    def get_absolute_url(self):
        return reverse('teachers-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'

class Grades(models.Model):
    EXAM_CHOICES = [
        ('неудовлетворительно', 'неудовлетворительно'),
        ('удовлетворительно', 'удовлетворительно'),
        ('хорошо', 'хорошо'),
        ('отлично', 'отлично'),
    ]
    TEST_CHOICES = [
        ('не зачтено', 'не зачтено'),
        ('зачтено', 'зачтено'),
    ]
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name='Студент')
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, verbose_name='Предмет')
    grade_exam = models.CharField('', max_length=20, choices=EXAM_CHOICES, blank=True)
    grade_test = models.CharField('', max_length=10, choices=TEST_CHOICES, blank=True)

    def __str__(self):
        return f"{self.student_id} - {self.subject_id}"

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

class Curriculum(models.Model):
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, verbose_name='Предмет')
    teacher_id = models.ForeignKey(Teachers, on_delete=models.CASCADE, verbose_name='Преподаватель')
    group_number = models.ForeignKey(Groups, on_delete=models.CASCADE, verbose_name='Группа')
    semester = models.IntegerField('Номер семестра')

    def __str__(self):
        return f"{self.subject_id} ({self.teacher_id}) - {self.group_number}"

    class Meta:
        verbose_name = 'Учебный план'
        verbose_name_plural = 'Учебный план'

