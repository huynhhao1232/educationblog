from homepage.models import Campus, Shift, SubjectGroup, CampusShiftGroup

# Tạo Campus
campus_main = Campus.objects.get_or_create(code="main", defaults={"name": "Trụ sở chính", "address": "153/1 Võ Văn Ngân, phường Linh Chiểu, thành phố Thủ Đức, Thành phố Hồ Chí Minh."})[0]
campus_cs1 = Campus.objects.get_or_create(code="cs1", defaults={"name": "Cơ sở 1", "address": "số 45 đường Phan Bá Vành, phường Thạnh Mỹ Lợi, thành phố Thủ Đức, Thành phố Hồ Chí Minh."})[0]
campus_cs2 = Campus.objects.get_or_create(code="cs2", defaults={"name": "Cơ sở 2", "address": "đường Đình Phong Phú, phường Tăng Nhơn Phú B, thành phố Thủ Đức, Thành phố Hồ Chí Minh."})[0]

# Tạo Shift
shift_sang = Shift.objects.get_or_create(code="sang", name="Ca sáng")[0]
shift_toi = Shift.objects.get_or_create(code="toi", name="Ca tối")[0]

# Danh sách tổ hợp môn
subject_groups_data = [
    ("1", "Ngữ văn*, Toán*, Lịch sử, Anh văn, Địa lý, Vật lý*, Hóa học, Tin học"),
    ("2", "Ngữ văn*, Toán*, Lịch sử, Anh văn, Địa lý, Hóa học*, Sinh học, Tin học"),
    ("3", "Ngữ văn*, Toán*, Lịch sử, Anh văn, Địa lý, Hóa học, KTPL*, Tin học"),
    ("4", "Ngữ văn*, Toán*, Lịch sử, Anh văn, Địa lý, Vật lý, Hóa học, Sinh học*"),
    ("5", "Ngữ văn*, Toán*, Lịch sử*, Anh văn, Vật lý, Hóa học, KTPL, Tin học")
]

subject_groups = {}
for code, subjects in subject_groups_data:
    group = SubjectGroup.objects.get_or_create(code=code, defaults={
        "description": f"Tổ hợp {code}",
        "subjects": subjects
    })[0]
    subject_groups[code] = group

# Tính số lượng cho phép: 50 học viên/lớp + 20%
def calc_capacity(classes):
    return int(classes * 50 * 1.2)

# Cấu hình dữ liệu theo yêu cầu
mapping = [
    # Trụ sở chính - ca sáng

    (campus_main, shift_sang, subject_groups["2"], 2),
    (campus_main, shift_sang, subject_groups["3"], 2),
    (campus_main, shift_sang, subject_groups["4"], 2),
    # Trụ sở chính - ca tối
    (campus_main, shift_toi, subject_groups["4"], 2),
    # Cơ sở 1 - ca sáng
    (campus_cs1, shift_sang, subject_groups["2"], 2),
    (campus_cs1, shift_sang, subject_groups["4"], 2),
    # Cơ sở 2 - ca sáng (giống cơ sở 1)
    (campus_cs2, shift_sang, subject_groups["2"], 2),
    (campus_cs2, shift_sang, subject_groups["4"], 2),
]

for campus, shift, group, num_classes in mapping:
    CampusShiftGroup.objects.update_or_create(
        campus=campus,
        shift=shift,
        subject_group=group,
        defaults={
            "number_of_classes": num_classes,
            "registration_count": calc_capacity(num_classes)
        }
    )

print("✅ Dữ liệu đã được cập nhật thành công theo yêu cầu.")
