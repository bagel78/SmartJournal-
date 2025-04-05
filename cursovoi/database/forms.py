from django.contrib.auth import authenticate
from django.db.models import ImageField

from .models import Students, Teachers, Grades
from django.forms import ModelForm, TextInput, Select, ClearableFileInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': 'username'
    }))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': 'password'
    }))
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': 'password'
    }))

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': 'username'
    }))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class':'form-control',
        'placeholder': 'password'
    }))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError('Неправильные имя пользователя или пароль')
        return self.cleaned_data

class UserPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={
        'class':'form-control'}))
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput(attrs={
        'class':'form-control'}))

    class Meta:
        fields = [ 'new_password1', 'new_password2']

class StudentsForm(ModelForm):

    class Meta:
        model = Students
        fields = ['photo', 'last_name', 'first_name', 'father_name', 'birth_date', 'gender', 'phone_number', 'group']
        widgets = {
            "photo": ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            "last_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов'
            }),
            "first_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван'
            }),
            "father_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванович'
            }),
            "birth_date": TextInput(attrs={
                'class': 'form-control',
                #'placeholder': 'Дата рождения',
                'type': 'date'
            }),
            "gender": Select(attrs={
                'class': 'form-select',
                #'placeholder': 'Пол'
            }),
            "phone_number": TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            "group": Select(attrs={
                'class': 'form-select',
                #'placeholder': 'Группа'
            })
        }

class TeachersForm(ModelForm):
    class Meta:
        model = Teachers
        fields = ['photo', 'last_name', 'first_name', 'father_name', 'birth_date', 'gender', 'phone_number', 'department_name', 'post']

        widgets = {
            "photo": ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            "last_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванов'
            }),
            "first_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иван'
            }),
            "father_name": TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Иванович'
            }),
            "birth_date": TextInput(attrs={
                'class': 'form-control',
                #'placeholder': 'Дата рождения',
                'type': 'date'
            }),
            "gender": Select(attrs={
                'class': 'form-select',
                #'placeholder': 'Пол'
            }),
            "phone_number": TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 (999) 123-45-67'
            }),
            "post": Select(attrs={
                'class': 'form-select',
                #'placeholder': 'Должность'
            }),
            "department_name": Select(attrs={
                'class': 'form-select',
                # 'placeholder': 'Кафедра'
            }),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grades
        fields = ['grade_exam', 'grade_test']
        widgets = {
            'grade_exam': Select(attrs={
                'class': 'form-select',
            }),
            'grade_test': Select(attrs={
                'class': 'form-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        assessment_form = kwargs.pop('assessment_form', None)
        super().__init__(*args, **kwargs)

        if assessment_form == 'Экзамен':
            del self.fields['grade_test']
        else:
            del self.fields['grade_exam']