"""
Script để tạo dữ liệu tổ hợp môn theo yêu cầu:
- Tổ hợp 01, 11: Lý, Hoá, Sử, Địa, Tin (+ Tiếng Anh cho 11)
- Tổ hợp 02, 12: Hoá, Sinh, Sử, Địa, Tin (+ Tiếng Anh cho 12)
- Tổ hợp 03, 13: Hoá, Sử, Địa, KTPL, Tin (+ Tiếng Anh cho 13)
- Tổ hợp 04, 14: Lý, Hoá, Sử, Địa, Sinh (+ Tiếng Anh cho 14)
- Tổ hợp 05, 15: Lý, Hoá, Sử, KTPT, Tin (+ Tiếng Anh cho 15)
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educationblog.settings')
django.setup()

from homepage.models import SubjectGroup

# Định nghĩa các tổ hợp môn
subject_groups_data = [
    # Tổ hợp 1 - Không có tiếng Anh
    {
        'code': '01',
        'description': 'Tổ hợp 1 (không có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, Địa, Tin'
    },
    # Tổ hợp 1 - Có tiếng Anh
    {
        'code': '11',
        'description': 'Tổ hợp 1 (có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, Địa, Tin, Tiếng Anh'
    },
    # Tổ hợp 2 - Không có tiếng Anh
    {
        'code': '02',
        'description': 'Tổ hợp 2 (không có tiếng Anh)',
        'subjects': 'Hoá, Sinh, Sử, Địa, Tin'
    },
    # Tổ hợp 2 - Có tiếng Anh
    {
        'code': '12',
        'description': 'Tổ hợp 2 (có tiếng Anh)',
        'subjects': 'Hoá, Sinh, Sử, Địa, Tin, Tiếng Anh'
    },
    # Tổ hợp 3 - Không có tiếng Anh
    {
        'code': '03',
        'description': 'Tổ hợp 3 (không có tiếng Anh)',
        'subjects': 'Hoá, Sử, Địa, KTPL, Tin'
    },
    # Tổ hợp 3 - Có tiếng Anh
    {
        'code': '13',
        'description': 'Tổ hợp 3 (có tiếng Anh)',
        'subjects': 'Hoá, Sử, Địa, KTPL, Tin, Tiếng Anh'
    },
    # Tổ hợp 4 - Không có tiếng Anh
    {
        'code': '04',
        'description': 'Tổ hợp 4 (không có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, Địa, Sinh'
    },
    # Tổ hợp 4 - Có tiếng Anh
    {
        'code': '14',
        'description': 'Tổ hợp 4 (có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, Địa, Sinh, Tiếng Anh'
    },
    # Tổ hợp 5 - Không có tiếng Anh
    {
        'code': '05',
        'description': 'Tổ hợp 5 (không có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, KTPT, Tin'
    },
    # Tổ hợp 5 - Có tiếng Anh
    {
        'code': '15',
        'description': 'Tổ hợp 5 (có tiếng Anh)',
        'subjects': 'Lý, Hoá, Sử, KTPT, Tin, Tiếng Anh'
    },
]

def seed_subject_groups():
    """Tạo hoặc cập nhật các tổ hợp môn"""
    created_count = 0
    updated_count = 0
    
    for group_data in subject_groups_data:
        group, created = SubjectGroup.objects.update_or_create(
            code=group_data['code'],
            defaults={
                'description': group_data['description'],
                'subjects': group_data['subjects']
            }
        )
        if created:
            created_count += 1
            print(f"✅ Đã tạo tổ hợp {group_data['code']}: {group_data['description']}")
        else:
            updated_count += 1
            print(f"🔄 Đã cập nhật tổ hợp {group_data['code']}: {group_data['description']}")
    
    print(f"\n📊 Tổng kết:")
    print(f"   - Đã tạo: {created_count} tổ hợp")
    print(f"   - Đã cập nhật: {updated_count} tổ hợp")
    print(f"   - Tổng số tổ hợp: {SubjectGroup.objects.count()}")

if __name__ == '__main__':
    print("🚀 Bắt đầu tạo dữ liệu tổ hợp môn...\n")
    seed_subject_groups()
    print("\n✅ Hoàn tất!")

