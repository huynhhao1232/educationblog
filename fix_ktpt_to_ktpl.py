#!/usr/bin/env python
"""
Script để đổi môn KTPT thành KTPL cho học viên trong tổ hợp 05 và 15

Cách sử dụng:
    python fix_ktpt_to_ktpl.py
    hoặc
    python manage.py shell < fix_ktpt_to_ktpl.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educationblog.settings')
django.setup()

from homepage.models import StudentExamRegistration, RegistrationHistory, Student, SubjectGroup

def fix_ktpt_to_ktpl():
    """Đổi môn KTPT thành KTPL cho học viên trong tổ hợp 05 và 15"""
    print("=" * 60)
    print("ĐỔI MÔN KTPT THÀNH KTPL")
    print("=" * 60)
    
    # Lấy tổ hợp 05 và 15
    try:
        subject_group_05 = SubjectGroup.objects.get(code='05')
        subject_group_15 = SubjectGroup.objects.get(code='15')
    except SubjectGroup.DoesNotExist:
        print("❌ Không tìm thấy tổ hợp 05 hoặc 15")
        return
    
    # Tìm tất cả học viên trong tổ hợp 05 và 15
    students_05_15 = Student.objects.filter(
        subject_group__in=[subject_group_05, subject_group_15]
    )
    
    # Tìm các đăng ký của học viên này có chọn KTPT
    registrations = StudentExamRegistration.objects.filter(
        student__in=students_05_15
    )
    
    updated_count = 0
    updated_registrations = []
    
    print(f"\nĐang kiểm tra {registrations.count()} đăng ký...")
    
    for registration in registrations:
        if registration.exam_subjects and isinstance(registration.exam_subjects, list):
            # Kiểm tra xem có KTPT không
            if 'KTPT' in registration.exam_subjects:
                # Tạo bản sao để so sánh
                old_subjects = registration.exam_subjects.copy()
                
                # Thay thế KTPT thành KTPL
                new_subjects = [subject if subject != 'KTPT' else 'KTPL' for subject in registration.exam_subjects]
                
                # Cập nhật
                registration.exam_subjects = new_subjects
                registration.save()
                
                updated_count += 1
                updated_registrations.append({
                    'registration': registration,
                    'old_subjects': old_subjects,
                    'new_subjects': new_subjects
                })
                
                print(f"✅ Đã cập nhật: {registration.student.student_code} - {registration.student.full_name}")
                print(f"   Tổ hợp: {registration.student.subject_group.code}")
                print(f"   Cũ: {old_subjects}")
                print(f"   Mới: {new_subjects}")
    
    # Cập nhật lịch sử nếu có
    history_updated = 0
    for item in updated_registrations:
        registration_obj = item['registration']
        # Cập nhật các bản ghi lịch sử có chứa KTPT
        histories = RegistrationHistory.objects.filter(registration=registration_obj)
        for history in histories:
            updated = False
            
            # Cập nhật old_exam_subjects
            if history.old_exam_subjects and isinstance(history.old_exam_subjects, list):
                if 'KTPT' in history.old_exam_subjects:
                    history.old_exam_subjects = [s if s != 'KTPT' else 'KTPL' for s in history.old_exam_subjects]
                    updated = True
            
            # Cập nhật new_exam_subjects
            if history.new_exam_subjects and isinstance(history.new_exam_subjects, list):
                if 'KTPT' in history.new_exam_subjects:
                    history.new_exam_subjects = [s if s != 'KTPT' else 'KTPL' for s in history.new_exam_subjects]
                    updated = True
            
            if updated:
                history.save()
                history_updated += 1
    
    print("\n" + "=" * 60)
    print("✅ HOÀN TẤT!")
    print("=" * 60)
    print(f"\nTổng số đăng ký đã cập nhật: {updated_count}")
    print(f"Tổng số lịch sử đã cập nhật: {history_updated}")
    
    if updated_count > 0:
        print(f"\n📋 Danh sách đã cập nhật:")
        for item in updated_registrations:
            reg = item['registration']
            print(f"  - {reg.student.student_code}: {item['old_subjects']} → {item['new_subjects']}")
    else:
        print("\n⚠️  Không tìm thấy đăng ký nào có môn KTPT trong tổ hợp 05 và 15")

if __name__ == '__main__':
    confirm = input("\n⚠️  BẠN CÓ CHẮC CHẮN MUỐN ĐỔI KTPT THÀNH KTPL? (gõ 'YES' để xác nhận): ")
    
    if confirm == 'YES':
        fix_ktpt_to_ktpl()
    else:
        print("\n❌ Đã hủy. Không có dữ liệu nào bị thay đổi.")

