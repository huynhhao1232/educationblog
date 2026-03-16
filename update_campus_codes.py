"""
Script để cập nhật mã cơ sở theo dữ liệu mới
Dựa trên bảng: 
10=AT (Trụ sở chính), 11=BS (Cơ sở 1), 12=CS (Cơ sở 2), 
13=ĐS (Trường Trung cấp Đông Sài Gòn), 
14=CN (Trường Cao đẳng Công nghệ Thành phố Hồ Chí Minh), 
15=VH (Trường Cao đẳng Kỹ Nghệ II), 
16=HT (Trung tâm Huấn luyện Thể thao Quốc gia), 
17=KT (Trường Cao đẳng Kinh tế Kỹ thuật Thủ Đức)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educationblog.settings')
django.setup()

from homepage.models import Campus

# Định nghĩa mã cơ sở mới
# Format: (mã_số, mã_code, tên_cơ_sở, địa_chỉ)
campus_data = [
    (10, "AT", "Trụ sở chính", "153/1 Võ Văn Ngân, phường Linh Chiểu, thành phố Thủ Đức, Thành phố Hồ Chí Minh."),
    (11, "BS", "Cơ sở 1", "số 45 đường Phan Bá Vành, phường Thạnh Mỹ Lợi, thành phố Thủ Đức, Thành phố Hồ Chí Minh."),
    (12, "CS", "Cơ sở 2", "đường Đình Phong Phú, phường Tăng Nhơn Phú B, thành phố Thủ Đức, Thành phố Hồ Chí Minh."),
    (13, "ĐS", "Trường Trung cấp Đông Sài Gòn", ""),
    (14, "CN", "Trường Cao đẳng Công nghệ Thành phố Hồ Chí Minh", ""),
    (15, "VH", "Trường Cao đẳng Kỹ Nghệ II", ""),
    (16, "HT", "Trung tâm Huấn luyện Thể thao Quốc gia", ""),
    (17, "KT", "Trường Cao đẳng Kinh tế Kỹ thuật Thủ Đức", ""),
]

def update_campus_codes():
    """Cập nhật hoặc tạo mới mã cơ sở"""
    created_count = 0
    updated_count = 0
    error_count = 0
    
    # Mapping từ mã cũ sang mã mới
    old_to_new_mapping = {
        "main": "AT",
        "TSC": "AT",
        "cs1": "BS",
        "CS1": "BS",
        "cs2": "CS",
        "CS2": "CS"
    }
    
    # Cập nhật các cơ sở cũ
    from homepage.models import Student, AdmissionForm
    for old_code, new_code in old_to_new_mapping.items():
        try:
            old_campus = Campus.objects.filter(code=old_code).first()
            new_campus = Campus.objects.filter(code=new_code).first()
            
            if old_campus:
                if new_campus and new_campus.id != old_campus.id:
                    # Cập nhật tất cả học viên và đơn tuyển sinh trỏ đến cơ sở mới
                    Student.objects.filter(campus=old_campus).update(campus=new_campus)
                    AdmissionForm.objects.filter(campus=old_campus).update(campus=new_campus)
                    print(f"🔄 Đã chuyển học viên và đơn tuyển sinh từ {old_code} sang {new_code}")
                    # Xóa cơ sở cũ
                    old_campus.delete()
                    print(f"🗑️  Đã xóa cơ sở cũ: {old_code}")
                else:
                    # Cập nhật mã cơ sở
                    old_campus.code = new_code
                    old_campus.save()
                    updated_count += 1
                    print(f"🔄 Đã cập nhật mã cơ sở: {old_code} → {new_code}")
        except Exception as e:
            print(f"❌ Lỗi khi cập nhật {old_code}: {str(e)}")
            error_count += 1
    
    # Tạo hoặc cập nhật các cơ sở mới
    for num, code, name, address in campus_data:
        try:
            campus, created = Campus.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'address': address
                }
            )
            if created:
                created_count += 1
                print(f"✅ Đã tạo cơ sở mới: {code} - {name}")
            else:
                print(f"🔄 Đã cập nhật cơ sở: {code} - {name}")
        except Exception as e:
            print(f"❌ Lỗi khi xử lý cơ sở {code}: {str(e)}")
            error_count += 1
    
    print(f"\n📊 Tổng kết:")
    print(f"   - Đã tạo: {created_count} cơ sở")
    print(f"   - Đã cập nhật: {updated_count} cơ sở")
    print(f"   - Lỗi: {error_count} cơ sở")
    print(f"   - Tổng số cơ sở: {Campus.objects.count()}")
    
    # Xóa các cơ sở trùng lặp không cần thiết
    duplicate_codes = ["TruongT", "TruongC1", "TruongC2", "TrungTam", "Truong"]
    for dup_code in duplicate_codes:
        try:
            campus = Campus.objects.filter(code=dup_code).first()
            if campus:
                campus.delete()
                print(f"🗑️  Đã xóa cơ sở trùng lặp: {dup_code}")
        except Exception as e:
            print(f"❌ Lỗi khi xóa {dup_code}: {str(e)}")
    
    print(f"\n📋 Danh sách cơ sở hiện tại:")
    for campus in Campus.objects.all().order_by('code'):
        print(f"   - {campus.code}: {campus.name}")

if __name__ == '__main__':
    print("🚀 Bắt đầu cập nhật mã cơ sở...\n")
    update_campus_codes()
    print("\n✅ Hoàn tất!")

