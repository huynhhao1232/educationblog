#!/usr/bin/env python
"""
Script để xóa tất cả dữ liệu trong các bảng:
- RegistrationHistory
- StudentExamRegistration  
- Student

Cách sử dụng:
    python clear_registration_data.py
    hoặc
    python manage.py shell < clear_registration_data.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educationblog.settings')
django.setup()

from homepage.models import Student, StudentExamRegistration, RegistrationHistory

def clear_all_data():
    """Xóa tất cả dữ liệu trong 3 bảng"""
    print("=" * 60)
    print("XÓA DỮ LIỆU ĐĂNG KÝ THI TỐT NGHIỆP")
    print("=" * 60)
    
    # Đếm số lượng bản ghi trước khi xóa
    history_count = RegistrationHistory.objects.count()
    registration_count = StudentExamRegistration.objects.count()
    student_count = Student.objects.count()
    
    print(f"\nSố lượng bản ghi hiện tại:")
    print(f"  - RegistrationHistory: {history_count}")
    print(f"  - StudentExamRegistration: {registration_count}")
    print(f"  - Student: {student_count}")
    print(f"  - Tổng cộng: {history_count + registration_count + student_count}")
    
    # Xác nhận
    confirm = input("\n⚠️  BẠN CÓ CHẮC CHẮN MUỐN XÓA TẤT CẢ DỮ LIỆU? (gõ 'YES' để xác nhận): ")
    
    if confirm != 'YES':
        print("\n❌ Đã hủy. Không có dữ liệu nào bị xóa.")
        return
    
    try:
        # Xóa theo thứ tự để tránh lỗi foreign key
        print("\n🔄 Đang xóa dữ liệu...")
        
        # 1. Xóa RegistrationHistory trước (có foreign key đến StudentExamRegistration)
        deleted_history = RegistrationHistory.objects.all().delete()
        print(f"✅ Đã xóa {deleted_history[0]} bản ghi lịch sử")
        
        # 2. Xóa StudentExamRegistration (có foreign key đến Student)
        deleted_registration = StudentExamRegistration.objects.all().delete()
        print(f"✅ Đã xóa {deleted_registration[0]} bản ghi đăng ký")
        
        # 3. Xóa Student cuối cùng
        deleted_student = Student.objects.all().delete()
        print(f"✅ Đã xóa {deleted_student[0]} bản ghi học viên")
        
        print("\n" + "=" * 60)
        print("✅ XÓA DỮ LIỆU THÀNH CÔNG!")
        print("=" * 60)
        print(f"\nTổng số bản ghi đã xóa: {deleted_history[0] + deleted_registration[0] + deleted_student[0]}")
        
    except Exception as e:
        print(f"\n❌ CÓ LỖI XẢY RA: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    clear_all_data()

