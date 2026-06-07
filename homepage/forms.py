from django import forms
from .models import Student, StudentExamRegistration, SubjectGroup, StudentInfoVerification

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

class StudentInfoLookupForm(forms.Form):
    """Nhập mã học viên 7 số để kiểm tra thông tin."""

    student_code = forms.CharField(
        max_length=7,
        min_length=7,
        label="Mã học viên",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nhập mã 7 số",
                "pattern": "[0-9]{7}",
                "required": True,
            }
        ),
    )

    def clean_student_code(self):
        code = (self.cleaned_data.get("student_code") or "").strip()
        if not code.isdigit() or len(code) != 7:
            raise forms.ValidationError("Mã học viên phải đúng 7 chữ số.")
        return code


# Các trường được học viên xác nhận (value = tên field trên StudentInfoVerification)
STUDENT_INFO_VERIFIABLE_STATUS_FIELDS = (
    ("class_name_status", "Lớp"),
    ("full_name_status", "Họ và tên"),
    ("birthday_status", "Ngày sinh"),
    ("birth_place_status", "Nơi sinh"),
    ("gender_status", "Giới tính"),
    ("ethnicity_status", "Dân tộc"),
    ("id_number_status", "Số CCCD"),
    ("contact_address_status", "Địa chỉ liên hệ"),
    ("email_status", "Gmail"),
    ("phone_status", "Số điện thoại"),
    ("highschool_10_status", "Nơi học THPT lớp 10"),
    ("highschool_11_status", "Nơi học THPT lớp 11"),
    ("exam_subjects_status", "Môn thi TN THPT"),
)


class StudentInfoVerificationForm(forms.ModelForm):
    """Một lần xác nhận tổng thể; nếu có sai thì tick checkbox từng mục."""

    OVERALL_CHOICES = (
        ("all_ok", "Tất cả thông tin trên là đúng"),
        ("has_wrong", "Có một hoặc nhiều mục thông tin sai"),
    )

    overall = forms.ChoiceField(
        label="Xác nhận của bạn",
        choices=OVERALL_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "si-overall-radio"}),
        required=True,
    )
    wrong_fields = forms.MultipleChoiceField(
        label="Các mục thông tin bị sai (tick để chọn)",
        required=False,
        choices=[],  # set in __init__
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "form-check-input si-wrong-checkbox"}
        ),
    )

    class Meta:
        model = StudentInfoVerification
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Ghi chú thêm (khuyến nghị nếu có mục sai)",
                }
            ),
        }
        labels = {"note": "Ghi chú thêm (nếu có)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["wrong_fields"].choices = list(STUDENT_INFO_VERIFIABLE_STATUS_FIELDS)
        inst = self.instance
        if inst.pk:
            wrong_list = [
                attr
                for attr, _ in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS
                if getattr(inst, attr, "") == "S"
            ]
            all_d = all(
                getattr(inst, attr, "") == "D"
                for attr, _ in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS
            )
            if wrong_list:
                self.fields["overall"].initial = "has_wrong"
                self.fields["wrong_fields"].initial = wrong_list
            elif all_d:
                self.fields["overall"].initial = "all_ok"

    def clean(self):
        cleaned = super().clean()
        overall = cleaned.get("overall")
        wrong = list(cleaned.get("wrong_fields") or [])
        if overall == "all_ok":
            cleaned["wrong_fields"] = []
        elif overall == "has_wrong" and not wrong:
            raise forms.ValidationError(
                "Bạn đã chọn «Có thông tin sai». Vui lòng tick ít nhất một mục bị sai."
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        overall = self.cleaned_data["overall"]
        wrong = set(self.cleaned_data.get("wrong_fields") or [])
        for attr, _ in STUDENT_INFO_VERIFIABLE_STATUS_FIELDS:
            setattr(instance, attr, "S" if attr in wrong else "D")
        if commit:
            instance.save()
        return instance

