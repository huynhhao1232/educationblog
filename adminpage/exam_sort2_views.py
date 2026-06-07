"""Views cho chức năng Sắp xếp phòng thi II."""
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Max, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from adminpage.exam_sort2_logic import (
    ELECTIVE_BOC_THAM_LAYOUTS,
    assign_candidates_to_rooms,
    assign_exam_numbers_sort2,
    build_room_diagram_blocks,
    elective_pair_key,
    elective_pair_label,
    get_room_assignments_ordered,
    next_room_sort_order,
    parse_exam_sort2_import_rows,
    parse_exam_sort2_import_rooms,
    roster_pair_display_label,
    sort_exam_sort2_candidates_by_vi_name,
    sort_venue_candidates_for_display,
    _roster_pair_context,
)
from adminpage.exam_sort2_export import build_venue_export_workbook
from adminpage.exam_sort2_statistics import (
    build_all_statistics_workbook,
    build_elective_slot_counts_workbook,
    build_venue_elective_slot_counts_workbook,
    build_venue_statistics_workbook,
    exam_sort2_statistics_template_path,
)
from homepage.models import (
    Account,
    AccountType,
    Campus,
    ExamSort2Candidate,
    ExamSort2Room,
    ExamSort2SeatAssignment,
    ExamSort2Venue,
    ExamSort2VenueCandidate,
)


def _require_admin(request):
    if not request.user.is_authenticated:
        return redirect('homepage:login')
    account = Account.objects.get(user=request.user)
    accounttype = AccountType.objects.get(accounttype_id=account.accounttype.accounttype_id)
    if accounttype.accounttype_role != 'admin':
        return redirect('homepage:Homepage')
    return None


def exam_sort2_candidates(request):
    """Phân hệ 1: quản lý danh sách thí sinh."""
    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'add':
            full_name = (request.POST.get('full_name') or '').strip()
            class_name = (request.POST.get('class_name') or '').strip()
            campus_id = request.POST.get('campus_id')
            if not full_name or not class_name or not campus_id:
                messages.error(request, 'Vui lòng nhập đủ Họ tên, Cơ sở và Lớp.')
            else:
                campus = get_object_or_404(Campus, pk=campus_id)
                e1 = (request.POST.get('elective_subject_1') or '').strip()
                e2 = (request.POST.get('elective_subject_2') or '').strip()
                ExamSort2Candidate.objects.create(
                    full_name=full_name,
                    class_name=class_name,
                    campus=campus,
                    elective_subject_1=e1,
                    elective_subject_2=e2,
                )
                messages.success(request, f'Đã thêm thí sinh {full_name}.')
            return redirect('adminpage:exam_sort2_candidates')

        if action == 'delete':
            pk = request.POST.get('candidate_id')
            if pk:
                ExamSort2Candidate.objects.filter(pk=pk).delete()
                messages.success(request, 'Đã xóa thí sinh.')
            return redirect('adminpage:exam_sort2_candidates')

        if action == 'delete_all':
            total_all = ExamSort2Candidate.objects.count()
            if total_all == 0:
                messages.info(request, 'Danh sách thí sinh đã trống.')
            else:
                with transaction.atomic():
                    ExamSort2Candidate.objects.all().delete()
                request.session.pop('exam_sort2_import_rows', None)
                request.session.pop('exam_sort2_import_errors', None)
                messages.success(
                    request,
                    f'Đã xóa toàn bộ {total_all} thí sinh '
                    f'(gồm liên kết tại điểm thi và xếp ghế).',
                )
            return redirect('adminpage:exam_sort2_candidates')

    q = (request.GET.get('q') or '').strip()
    campus_filter = request.GET.get('campus_id', '')
    candidates = ExamSort2Candidate.objects.select_related('campus').all()
    if campus_filter:
        candidates = candidates.filter(campus_id=campus_filter)
    if q:
        candidates = candidates.filter(
            Q(full_name__icontains=q) | Q(class_name__icontains=q)
        )
    campuses = Campus.objects.order_by('code')
    candidate_total = ExamSort2Candidate.objects.count()

    context = {
        'candidates': candidates,
        'campuses': campuses,
        'filter_campus': campus_filter,
        'search_q': q,
        'total': candidates.count(),
        'candidate_total': candidate_total,
        'has_candidates': candidate_total > 0,
    }
    return render(request, 'adminpageSIMCODE/exam_sort2_candidates.html', context)


def exam_sort2_import_candidates(request):
    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == 'POST' and request.FILES.get('excel_file'):
        f = request.FILES['excel_file']
        try:
            rows, errors = parse_exam_sort2_import_rows(f, f.name)
        except Exception as exc:  # noqa: BLE001
            return render(request, 'adminpageSIMCODE/exam_sort2_import_preview.html', {
                'rows': [],
                'errors': [f'Không đọc được file: {exc}'],
                'total_count': 0,
            })
        request.session['exam_sort2_import_rows'] = rows
        request.session['exam_sort2_import_errors'] = errors
        return render(request, 'adminpageSIMCODE/exam_sort2_import_preview.html', {
            'rows': rows,
            'errors': errors,
            'total_count': len(rows),
        })

    return redirect('adminpage:exam_sort2_candidates')


def exam_sort2_save_import(request):
    denied = _require_admin(request)
    if denied:
        return denied

    if request.method != 'POST':
        return redirect('adminpage:exam_sort2_candidates')

    rows = request.session.pop('exam_sort2_import_rows', None)
    request.session.pop('exam_sort2_import_errors', None)
    if not rows:
        messages.warning(request, 'Không có dữ liệu import trong phiên làm việc.')
        return redirect('adminpage:exam_sort2_candidates')

    created = 0
    with transaction.atomic():
        for row in rows:
            campus = Campus.objects.get(pk=row['campus_id'])
            ExamSort2Candidate.objects.create(
                full_name=row['full_name'],
                class_name=row['class_name'],
                campus=campus,
                elective_subject_1=row.get('elective_subject_1', ''),
                elective_subject_2=row.get('elective_subject_2', ''),
            )
            created += 1
    messages.success(request, f'Đã import {created} thí sinh.')
    return redirect('adminpage:exam_sort2_candidates')


def exam_sort2_venues(request):
    """Phân hệ 2: danh sách điểm thi."""
    denied = _require_admin(request)
    if denied:
        return denied

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'add':
            code = (request.POST.get('code') or '').strip()
            name = (request.POST.get('name') or '').strip()
            try:
                sort_order = int(request.POST.get('sort_order') or 0)
            except ValueError:
                sort_order = 0
            if not code or not name:
                messages.error(request, 'Vui lòng nhập Mã và Tên điểm thi.')
            elif ExamSort2Venue.objects.filter(code=code).exists():
                messages.error(request, f'Mã điểm thi "{code}" đã tồn tại.')
            else:
                ExamSort2Venue.objects.create(code=code, name=name, sort_order=sort_order)
                messages.success(request, f'Đã thêm điểm thi {code}.')
            return redirect('adminpage:exam_sort2_venues')

        if action == 'delete':
            pk = request.POST.get('venue_id')
            if pk:
                ExamSort2Venue.objects.filter(pk=pk).delete()
                messages.success(request, 'Đã xóa điểm thi và dữ liệu liên quan.')
            return redirect('adminpage:exam_sort2_venues')

        if action == 'edit':
            pk = request.POST.get('venue_id')
            code = (request.POST.get('code') or '').strip()
            name = (request.POST.get('name') or '').strip()
            try:
                sort_order = int(request.POST.get('sort_order') or 0)
            except ValueError:
                sort_order = 0
            if not pk or not code or not name:
                messages.error(request, 'Vui lòng nhập đủ Mã, Tên điểm thi.')
            else:
                venue = ExamSort2Venue.objects.filter(pk=pk).first()
                if not venue:
                    messages.error(request, 'Không tìm thấy điểm thi.')
                elif (
                    ExamSort2Venue.objects.filter(code=code).exclude(pk=venue.pk).exists()
                ):
                    messages.error(request, f'Mã điểm thi "{code}" đã được dùng.')
                else:
                    venue.code = code
                    venue.name = name
                    venue.sort_order = sort_order
                    venue.save()
                    messages.success(request, f'Đã cập nhật điểm thi {code}.')
            return redirect('adminpage:exam_sort2_venues')

        if action == 'assign_exam_numbers':
            try:
                start_serial = int(request.POST.get('sbd_start') or 0)
            except ValueError:
                start_serial = 0
            city_prefix = (request.POST.get('sbd_city_prefix') or '').strip()
            result = assign_exam_numbers_sort2(
                start_serial=start_serial if start_serial > 0 else None,
                city_prefix=city_prefix or None,
            )
            for err in result.get('errors', []):
                messages.error(request, err)
            if result.get('assigned'):
                messages.success(
                    request,
                    f'Đã sắp {result.get("rooms_reordered", 0)} phòng (mọi điểm thi) theo họ tên (TV), '
                    f'rồi đánh SBD cho {result["assigned"]} thí sinh toàn hệ thống '
                    f'({result.get("first_sbd")} → {result.get("last_sbd")}). '
                    f'Thứ tự: STT điểm thi → STT phòng → họ tên (TV).',
                )
            else:
                messages.warning(request, 'Không có thí sinh đã xếp ghế để đánh SBD.')
            return redirect('adminpage:exam_sort2_venues')

    venues = ExamSort2Venue.objects.annotate(
        candidate_count=Count('venue_candidates'),
        room_count=Count('rooms'),
    )
    seated_count = ExamSort2SeatAssignment.objects.count()
    context = {
        'venues': venues,
        'seated_count': seated_count,
        'exam_sort2_sbd_city_prefix': getattr(settings, 'EXAM_SORT2_SBD_CITY_PREFIX', '79'),
        'exam_sort2_sbd_start': getattr(settings, 'EXAM_SORT2_SBD_START_SERIAL', 1),
    }
    return render(request, 'adminpageSIMCODE/exam_sort2_venues.html', context)


def exam_sort2_venue_detail(request, venue_id: int):
    """Chi tiết điểm thi: layout trái (thí sinh) + phải (phòng & xếp chỗ)."""
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'pick_candidates':
            ids = request.POST.getlist('candidate_ids')
            if not ids:
                messages.warning(request, 'Chưa chọn thí sinh nào.')
            else:
                existing = set(
                    ExamSort2VenueCandidate.objects.filter(venue=venue)
                    .values_list('candidate_id', flat=True)
                )
                added = 0
                for cid in ids:
                    try:
                        cid_int = int(cid)
                    except ValueError:
                        continue
                    if cid_int in existing:
                        continue
                    if ExamSort2Candidate.objects.filter(pk=cid_int).exists():
                        ExamSort2VenueCandidate.objects.create(venue=venue, candidate_id=cid_int)
                        existing.add(cid_int)
                        added += 1
                messages.success(
                    request,
                    f'Đã lấy {added} thí sinh về điểm thi. '
                    f'Danh sách bên trái sắp theo bảng chữ cái TV (tên → đệm → họ).',
                )
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'remove_venue_candidate':
            vc_id = request.POST.get('venue_candidate_id')
            if vc_id:
                ExamSort2VenueCandidate.objects.filter(pk=vc_id, venue=venue).delete()
                messages.success(request, 'Đã gỡ thí sinh khỏi điểm thi.')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'delete_all_venue_candidates':
            vc_qs = ExamSort2VenueCandidate.objects.filter(venue=venue)
            vc_count = vc_qs.count()
            if vc_count == 0:
                messages.info(request, 'Điểm thi này chưa có thí sinh.')
            else:
                seat_count = ExamSort2SeatAssignment.objects.filter(room__venue=venue).count()
                vc_qs.delete()
                messages.success(
                    request,
                    f'Đã gỡ hết {vc_count} thí sinh khỏi điểm thi {venue.code} '
                    f'(đã xóa {seat_count} xếp ghế). '
                    f'Danh sách master thí sinh (SXPT II) vẫn giữ nguyên.',
                )
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'add_room':
            name = (request.POST.get('room_name') or '').strip()
            target_campus_id = request.POST.get('target_campus_id')
            try:
                col_count = max(1, int(request.POST.get('col_count') or 1))
                row_count = max(1, int(request.POST.get('row_count') or 1))
            except ValueError:
                messages.error(request, 'Số cột/hàng không hợp lệ.')
                return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)
            if not name or not target_campus_id:
                messages.error(request, 'Vui lòng nhập tên phòng và đối tượng cơ sở.')
            elif ExamSort2Room.objects.filter(venue=venue, name=name).exists():
                messages.error(request, f'Phòng "{name}" đã tồn tại tại điểm thi này.')
            else:
                try:
                    room_stt = int(request.POST.get('sort_order') or 0)
                except ValueError:
                    room_stt = 0
                if room_stt <= 0:
                    room_stt = next_room_sort_order(venue)
                ExamSort2Room.objects.create(
                    venue=venue,
                    name=name,
                    col_count=col_count,
                    row_count=row_count,
                    target_campus_id=target_campus_id,
                    sort_order=room_stt,
                )
                messages.success(request, f'Đã thêm phòng {name} (STT {room_stt}).')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'delete_room':
            room_id = request.POST.get('room_id')
            if room_id:
                ExamSort2Room.objects.filter(pk=room_id, venue=venue).delete()
                messages.success(request, 'Đã xóa phòng thi.')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'delete_all_rooms':
            room_qs = ExamSort2Room.objects.filter(venue=venue)
            room_count_del = room_qs.count()
            if room_count_del == 0:
                messages.info(request, 'Điểm thi này chưa có phòng thi.')
            else:
                seat_count = ExamSort2SeatAssignment.objects.filter(room__venue=venue).count()
                room_qs.delete()
                messages.success(
                    request,
                    f'Đã xóa {room_count_del} phòng thi tại {venue.code} '
                    f'(gồm {seat_count} xếp ghế). Thí sinh vẫn còn trong danh sách điểm thi.',
                )
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'edit_venue':
            code = (request.POST.get('code') or '').strip()
            name = (request.POST.get('name') or '').strip()
            try:
                sort_order = int(request.POST.get('sort_order') or 0)
            except ValueError:
                sort_order = 0
            if not code or not name:
                messages.error(request, 'Vui lòng nhập đủ Mã và Tên điểm thi.')
            elif ExamSort2Venue.objects.filter(code=code).exclude(pk=venue.pk).exists():
                messages.error(request, f'Mã điểm thi "{code}" đã được dùng.')
            else:
                venue.code = code
                venue.name = name
                venue.sort_order = sort_order
                venue.save()
                messages.success(request, f'Đã cập nhật điểm thi {code}.')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'edit_room':
            room_id = request.POST.get('room_id')
            name = (request.POST.get('room_name') or '').strip()
            target_campus_id = request.POST.get('target_campus_id')
            try:
                col_count = max(1, int(request.POST.get('col_count') or 1))
                row_count = max(1, int(request.POST.get('row_count') or 1))
            except ValueError:
                messages.error(request, 'Số cột/hàng không hợp lệ.')
                return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)
            room = ExamSort2Room.objects.filter(pk=room_id, venue=venue).first()
            if not room:
                messages.error(request, 'Không tìm thấy phòng thi.')
            elif not name or not target_campus_id:
                messages.error(request, 'Vui lòng nhập tên phòng và đối tượng cơ sở.')
            elif ExamSort2Room.objects.filter(venue=venue, name=name).exclude(pk=room.pk).exists():
                messages.error(request, f'Phòng "{name}" đã tồn tại tại điểm thi này.')
            else:
                new_capacity = col_count * row_count
                seat_count = ExamSort2SeatAssignment.objects.filter(room=room).count()
                max_seat = (
                    ExamSort2SeatAssignment.objects.filter(room=room)
                    .aggregate(m=Max('seat_number'))['m']
                    or 0
                )
                if seat_count and new_capacity < max_seat:
                    messages.error(
                        request,
                        f'Không thể thu nhỏ phòng: đang có ghế #{max_seat}, '
                        f'sức chứa mới chỉ {new_capacity} chỗ. Xóa xếp chỗ hoặc tăng kích thước.',
                    )
                else:
                    try:
                        room_stt = int(request.POST.get('sort_order') or 0)
                    except ValueError:
                        room_stt = room.sort_order
                    room.name = name
                    room.col_count = col_count
                    room.row_count = row_count
                    room.target_campus_id = target_campus_id
                    room.sort_order = max(0, room_stt)
                    room.save()
                    messages.success(request, f'Đã cập nhật phòng {name}.')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

        if action == 'assign_seats':
            clear = request.POST.get('clear_existing') == '1'
            result = assign_candidates_to_rooms(venue, clear_existing=clear)
            total = result['assigned_total']
            rooms_reordered = result.get('rooms_reordered', 0)
            for info in result.get('target_avg_info', []):
                messages.info(request, info)
            room_summaries = []
            for pr in result.get('per_room', []):
                if pr.get('filled'):
                    combos = pr.get('elective_combos') or []
                    combo_txt = '; '.join(combos[:3])
                    if len(combos) > 3:
                        combo_txt += '…'
                    room_summaries.append(
                        f"{pr['room_name']}: {pr['filled']}/{pr['capacity']} TS, "
                        f"{pr.get('elective_combo_count', 0)} tổ hợp ({combo_txt or '—'})",
                    )
            if room_summaries:
                messages.info(request, ' | '.join(room_summaries[:12]))
            if result['errors']:
                for err in result['errors']:
                    messages.warning(request, err)
            if total or rooms_reordered:
                msg = (
                    f'Đã xếp {total} thí sinh mới (tối thiểu 24/phòng, tối đa 3 tổ hợp, HV từ trên xuống). '
                    f'Đã sắp STT ghế {rooms_reordered} phòng theo họ tên (TV). '
                    f'Khi xong mọi điểm thi, bấm «Đánh SBD (toàn hệ thống)» trên danh sách điểm thi.'
                )
                messages.success(request, msg)
            else:
                messages.info(request, 'Không có thí sinh mới được xếp (phòng đầy hoặc không còn thí sinh phù hợp).')
            return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    venue_candidates = sort_venue_candidates_for_display(
        list(
            ExamSort2VenueCandidate.objects.filter(venue=venue).select_related(
                'candidate', 'candidate__campus',
            ),
        ),
    )
    assigned_vc_ids = set(
        ExamSort2SeatAssignment.objects.filter(room__venue=venue)
        .values_list('venue_candidate_id', flat=True)
    )

    rooms = ExamSort2Room.objects.filter(venue=venue).select_related('target_campus').order_by(
        'sort_order', 'name',
    )
    room_blocks = []
    for room in rooms:
        assignments = ExamSort2SeatAssignment.objects.filter(room=room).select_related(
            'venue_candidate__candidate',
        )
        seat_count = assignments.count()
        combo_keys = {
            elective_pair_key(a.venue_candidate.candidate) for a in assignments
        }
        room_blocks.append({
            'room': room,
            'seat_count': seat_count,
            'elective_combo_count': len(combo_keys),
            'elective_combos': sorted(
                {elective_pair_label(k) for k in combo_keys},
                key=lambda s: s.casefold(),
            ),
        })

    already_at_venue = {vc.candidate_id for vc in venue_candidates}
    pick_q = (request.GET.get('pick_q') or '').strip()
    pick_campus = request.GET.get('pick_campus', '')
    available = ExamSort2Candidate.objects.select_related('campus').exclude(pk__in=already_at_venue)
    if pick_campus:
        available = available.filter(campus_id=pick_campus)
    if pick_q:
        available = available.filter(
            Q(full_name__icontains=pick_q) | Q(class_name__icontains=pick_q)
        )
    available = sort_exam_sort2_candidates_by_vi_name(list(available))[:200]

    candidate_count = ExamSort2VenueCandidate.objects.filter(venue=venue).count()
    room_count = rooms.count()
    total_capacity = sum(room.col_count * room.row_count for room in rooms)
    assigned_seat_count = ExamSort2SeatAssignment.objects.filter(room__venue=venue).count()
    unassigned_count = max(candidate_count - len(assigned_vc_ids), 0)

    context = {
        'venue': venue,
        'venue_candidates': venue_candidates,
        'assigned_vc_ids': assigned_vc_ids,
        'candidate_count': candidate_count,
        'unassigned_count': unassigned_count,
        'assigned_seat_count': assigned_seat_count,
        'room_count': room_count,
        'total_capacity': total_capacity,
        'rooms': rooms,
        'room_blocks': room_blocks,
        'campuses': Campus.objects.order_by('code'),
        'pick_candidates': list(available),
        'pick_q': pick_q,
        'pick_campus': pick_campus,
        'open_pick_modal': request.GET.get('open_pick') == '1' or bool(pick_campus or pick_q),
        'next_room_stt': next_room_sort_order(venue),
    }
    return render(request, 'adminpageSIMCODE/exam_sort2_venue_detail.html', context)


def exam_sort2_room_detail(request, room_id: int):
    """Trang chi tiết phòng: trái sơ đồ 4 môn, phải danh sách thí sinh."""
    denied = _require_admin(request)
    if denied:
        return denied

    room = get_object_or_404(
        ExamSort2Room.objects.select_related('venue', 'target_campus'),
        pk=room_id,
    )
    assignments = get_room_assignments_ordered(room)
    subject_slots, subject_weights = _roster_pair_context(
        [a.venue_candidate.candidate for a in assignments],
    )
    students = []
    for a in assignments:
        cand = a.venue_candidate.candidate
        pair_label = roster_pair_display_label(
            cand,
            subject_slots=subject_slots,
            subject_weights=subject_weights,
        )
        students.append({
            'seat_number': a.seat_number,
            'exam_number': cand.exam_number or '',
            'full_name': cand.full_name,
            'class_name': cand.class_name,
            'campus_code': cand.campus.code,
            'campus_name': cand.campus.name,
            'elective_1': cand.elective_subject_1,
            'elective_2': cand.elective_subject_2,
            'elective_pair': pair_label,
            'exam_subjects': cand.get_exam_subjects_display(),
        })

    try:
        elective_layout_id = int(request.GET.get('so_do', '0'))
    except (TypeError, ValueError):
        elective_layout_id = 0
    if elective_layout_id not in ELECTIVE_BOC_THAM_LAYOUTS:
        elective_layout_id = 0

    context = {
        'room': room,
        'venue': room.venue,
        'subject_blocks': build_room_diagram_blocks(room, elective_layout_id=elective_layout_id),
        'elective_layout_id': elective_layout_id,
        'elective_boc_tham_layouts': ELECTIVE_BOC_THAM_LAYOUTS,
        'students': students,
        'seat_count': len(students),
    }
    return render(request, 'adminpageSIMCODE/exam_sort2_room_detail.html', context)


def _exam_sort2_phongthi_sample_path() -> Path:
    return Path(settings.BASE_DIR) / 'Sắp xếp phòng thi II' / 'phongthi.xlsx'


def exam_sort2_phongthi_template(request):
    """Tải file mẫu phongthi.xlsx trong project."""
    denied = _require_admin(request)
    if denied:
        return denied

    sample = _exam_sort2_phongthi_sample_path()
    if sample.is_file():
        return FileResponse(
            open(sample, 'rb'),
            as_attachment=True,
            filename='phongthi.xlsx',
        )

    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.append(['Tên Phòng', 'Số cột', 'Số hàng', 'Đối tượng', 'STT'])
    ws.append(['1A', 4, 7, 'AS', 1])
    ws.append(['2A', 4, 7, 'AS', 2])
    from io import BytesIO
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='phongthi_mau.xlsx')


def exam_sort2_import_rooms(request, venue_id: int):
    """Upload Excel phòng thi → xem trước."""
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)

    if request.method == 'POST' and request.FILES.get('excel_file'):
        f = request.FILES['excel_file']
        try:
            rows, errors = parse_exam_sort2_import_rooms(f, f.name)
        except Exception as exc:  # noqa: BLE001
            return render(request, 'adminpageSIMCODE/exam_sort2_rooms_import_preview.html', {
                'venue': venue,
                'rows': [],
                'errors': [f'Không đọc được file: {exc}'],
                'total_count': 0,
            })

        existing_names = set(
            ExamSort2Room.objects.filter(venue=venue).values_list('name', flat=True)
        )
        for row in rows:
            if row['name'] in existing_names:
                errors.append(
                    f"Dòng {row['row_number']}: Phòng \"{row['name']}\" đã tồn tại tại điểm thi này.",
                )

        request.session['exam_sort2_rooms_import_data'] = rows
        request.session['exam_sort2_rooms_import_venue_id'] = venue.id
        request.session['exam_sort2_rooms_import_errors'] = errors

        return render(request, 'adminpageSIMCODE/exam_sort2_rooms_import_preview.html', {
            'venue': venue,
            'rows': rows,
            'errors': errors,
            'total_count': len(rows),
        })

    return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)


def exam_sort2_save_rooms_import(request, venue_id: int):
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)

    if request.method != 'POST':
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    session_venue_id = request.session.get('exam_sort2_rooms_import_venue_id')
    if session_venue_id != venue.id:
        messages.warning(request, 'Phiên import không khớp điểm thi. Vui lòng upload lại file.')
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    rows = request.session.pop('exam_sort2_rooms_import_data', None)
    request.session.pop('exam_sort2_rooms_import_errors', None)
    request.session.pop('exam_sort2_rooms_import_venue_id', None)

    if not rows:
        messages.warning(request, 'Không có dữ liệu import.')
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    created = 0
    skipped = 0
    with transaction.atomic():
        existing_names = set(
            ExamSort2Room.objects.filter(venue=venue).values_list('name', flat=True)
        )
        next_stt = next_room_sort_order(venue)
        for row in rows:
            if row['name'] in existing_names:
                skipped += 1
                continue
            stt = int(row.get('sort_order') or 0)
            if stt <= 0:
                stt = next_stt
            ExamSort2Room.objects.create(
                venue=venue,
                name=row['name'],
                col_count=row['col_count'],
                row_count=row['row_count'],
                target_campus_id=row['target_campus_id'],
                sort_order=stt,
            )
            existing_names.add(row['name'])
            next_stt = max(next_stt, stt + 1)
            created += 1

    msg = f'Đã import {created} phòng thi.'
    if skipped:
        msg += f' Bỏ qua {skipped} phòng trùng tên.'
    messages.success(request, msg)
    return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)


def exam_sort2_statistics_export_all(request):
    """Xuất thống kê tất cả điểm thi — mỗi điểm thi một sheet."""
    denied = _require_admin(request)
    if denied:
        return denied

    venues = list(ExamSort2Venue.objects.order_by('sort_order', 'code'))
    if not venues:
        messages.warning(request, 'Chưa có điểm thi để xuất thống kê.')
        return redirect('adminpage:exam_sort2_venues')

    try:
        buf = build_all_statistics_workbook(venues)
    except FileNotFoundError as exc:
        messages.error(request, str(exc))
        return redirect('adminpage:exam_sort2_venues')

    return FileResponse(
        buf,
        as_attachment=True,
        filename='Thong_ke_phong_thi_SXPT_II.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


def exam_sort2_venue_export_excel(request, venue_id: int):
    """Xuất danh sách + sơ đồ 4 môn cho tất cả phòng tại điểm thi (mẫu EXPORT_TEMPLATE)."""
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)
    try:
        elective_layout_id = int(request.GET.get('so_do', '0'))
    except (TypeError, ValueError):
        elective_layout_id = 0
    if elective_layout_id not in ELECTIVE_BOC_THAM_LAYOUTS:
        elective_layout_id = 0
    elective_all_pa = request.GET.get('tc_pa', '').strip() in ('1', 'true', 'all')

    try:
        buf = build_venue_export_workbook(
            venue,
            elective_layout_id=elective_layout_id,
            elective_all_pa=elective_all_pa,
        )
    except FileNotFoundError as exc:
        messages.error(request, str(exc))
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)
    except ValueError as exc:
        messages.warning(request, str(exc))
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    safe_code = ''.join(c if c.isalnum() or c in '-_' else '_' for c in venue.code)
    return FileResponse(
        buf,
        as_attachment=True,
        filename=f'SXPT2_{safe_code}_danh_sach_so_do.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


def exam_sort2_elective_counts_export_all(request):
    """Xuất thống kê số lượng môn TC theo vị trí môn 1 / môn 2 — tất cả điểm thi."""
    denied = _require_admin(request)
    if denied:
        return denied

    venues = list(ExamSort2Venue.objects.order_by('sort_order', 'code'))
    if not venues:
        messages.warning(request, 'Chưa có điểm thi để xuất thống kê.')
        return redirect('adminpage:exam_sort2_venues')

    buf = build_elective_slot_counts_workbook(venues)
    return FileResponse(
        buf,
        as_attachment=True,
        filename='Thong_ke_mon_tu_chon_SXPT_II.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


def exam_sort2_elective_counts_export_venue(request, venue_id: int):
    """Xuất thống kê số lượng môn TC (2 sheet Môn 1 / Môn 2) cho một điểm thi."""
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)
    buf = build_venue_elective_slot_counts_workbook(venue)
    safe_code = ''.join(c if c.isalnum() or c in '-_' else '_' for c in venue.code)
    return FileResponse(
        buf,
        as_attachment=True,
        filename=f'Thong_ke_mon_TC_{safe_code}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


def exam_sort2_statistics_export_venue(request, venue_id: int):
    """Xuất thống kê một điểm thi (một sheet)."""
    denied = _require_admin(request)
    if denied:
        return denied

    venue = get_object_or_404(ExamSort2Venue, pk=venue_id)
    if not exam_sort2_statistics_template_path().is_file():
        messages.error(request, 'Không tìm thấy file mẫu thống kê trong thư mục project.')
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    try:
        buf = build_venue_statistics_workbook(venue)
    except FileNotFoundError as exc:
        messages.error(request, str(exc))
        return redirect('adminpage:exam_sort2_venue_detail', venue_id=venue.id)

    safe_code = ''.join(c if c.isalnum() or c in '-_' else '_' for c in venue.code)
    return FileResponse(
        buf,
        as_attachment=True,
        filename=f'Thong_ke_{safe_code}.xlsx',
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
