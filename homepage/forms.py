from django import forms
from .models import Student, StudentExamRegistration, SubjectGroup

class StudentCodeForm(forms.Form):
    """Form nhập mã học viên"""
    student_code = forms.CharField(
        max_length=7,
        min_length=7,
        label="Mã học viên",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã học viên (7 số)',
            'pattern': '[0-9]{7}',
            'required': True
        }),
        help_text="Mã học viên gồm 7 số: 2 số đầu (cơ sở), 2 số tiếp (tổ hợp môn), 3 số cuối (số thứ tự)"
    )

    def clean_student_code(self):
        student_code = self.cleaned_data.get('student_code')
        if not student_code.isdigit():
            raise forms.ValidationError("Mã học viên chỉ được chứa số")
        if len(student_code) != 7:
            raise forms.ValidationError("Mã học viên phải có đúng 7 số")
        return student_code


class StudentExamRegistrationForm(forms.ModelForm):
    """Form đăng ký thi tốt nghiệp"""
    exam_subjects = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input exam-subject-checkbox'}),
        label="Môn thi tốt nghiệp",
        required=True,
        help_text="Vui lòng chọn đúng 2 môn thi tốt nghiệp (bắt buộc)"
    )

    class Meta:
        model = StudentExamRegistration
        fields = ['email', 'phone', 'exam_subjects']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập địa chỉ email Gmail (ví dụ: example@gmail.com)',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại',
                'required': True
            }),
        }
        labels = {
            'email': 'Email',
            'phone': 'Số điện thoại',
        }

    def __init__(self, *args, **kwargs):
        subject_group = kwargs.pop('subject_group', None)
        super().__init__(*args, **kwargs)

        if subject_group and subject_group.subjects:
            # Lấy danh sách môn học từ tổ hợp môn
            subjects_list = [s.strip() for s in subject_group.subjects.split(',')]
            self.fields['exam_subjects'].choices = [(subject, subject) for subject in subjects_list]
        else:
            self.fields['exam_subjects'].choices = []

        # Nếu có instance (đang cập nhật), set giá trị initial cho exam_subjects
        if self.instance and self.instance.pk and self.instance.exam_subjects:
            self.fields['exam_subjects'].initial = self.instance.exam_subjects

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Kiểm tra email phải là gmail.com
            email_lower = email.lower().strip()
            if not email_lower.endswith('@gmail.com'):
                raise forms.ValidationError("Email phải là địa chỉ Gmail (@gmail.com). Vui lòng nhập email hợp lệ.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Số điện thoại chỉ được chứa số")
        return phone

    def clean_exam_subjects(self):
        exam_subjects = self.cleaned_data.get('exam_subjects')
        if not exam_subjects:
            raise forms.ValidationError("Vui lòng chọn môn thi tốt nghiệp")
        if len(exam_subjects) != 2:
            raise forms.ValidationError("Vui lòng chọn đúng 2 môn thi tốt nghiệp")
        return exam_subjects

