const menuItems = document.querySelectorAll('#menu .items li');
console.log(menuItems)
menuItems.forEach(item => {
    item.addEventListener('click', () => {
        // Xóa tất cả các lớp 'active' đang tồn tại trong các thẻ <li>
        menuItems.forEach(item => {
            item.classList.remove('active');
        });

        // Thêm lớp 'active' vào thẻ <li> đang được nhấn
        item.classList.add('active');
    });
});

// Hiển thị hình ảnh được chọn
// Xử lý khi chọn ảnh (image file)
// Kiểm tra xem phần tử có tồn tại không trước khi thêm sự kiện

// Khi người dùng thay đổi file





function openEditPost(postId) {
    const $modal = $('#exampleModal');
    $.ajax({
        url: `/adminpage/get-post-data/${postId}/`,  // Đường dẫn API
        method: 'GET',
        success: function(data) {
            console.log(data)
            // Điền dữ liệu vào form

            $modal.find('input[name="chapter_name"]').val(data.name); // Tên chương
            $modal.find('input[name="chapter_name"]').text(data.name); 
            $modal.find('input[name="post-id"]').val(data.id); 
            if (data.image) {
                $('#image-preview').html(`<img src="${data.image}" alt="Preview" style="max-width: 100%;"/>`);
            }
            CKEDITOR.instances['editor1'].setData(data.content); // Nội dung (CKEditor)
            $modal.find('input[name="action"]').val(2); // Đặt action = 1 (sửa)

            if (data.files.length > 0) {
                let fileList = '';
                const existingFiles = []; // Mảng lưu thông tin file
            
                data.files.forEach(file => {
                    const maxLength = 40; // Độ dài tối đa cho tên file
                    let displayName = file.name;
            
                    // Nếu tên file vượt quá độ dài cho phép, rút gọn
                    if (file.name.length > maxLength) {
                        displayName = file.name.substring(0, maxLength) + '...';
                    }
            
                    // Tạo danh sách hiển thị
                    fileList += `<a href="${file.url}" target="_blank" title="${file.name}">${displayName}</a><br>`;
            
                    // Thêm file vào mảng existingFiles
                    existingFiles.push(file.name); // Hoặc file.url nếu cần
                });
            
                // Hiển thị danh sách file trong giao diện
                $('#files-list').html(fileList);
            
                // Cập nhật giá trị input hidden
                $('#existing-files').val(JSON.stringify(existingFiles));
            }
            
            
            
            // Hiển thị trạng thái Công khai/Riêng tư
            if (data.enable) {
                $modal.find('.toggle').addClass('active');
                $modal.find('input[name="enableHidden"]').val(1);
            } else {
                $modal.find('.toggle').removeClass('active');
                $modal.find('input[name="enableHidden"]').val(0);
            }
            
            // Hiển thị modal
            $('#exampleModal').modal('show');
        },
        error: function() {
            alert('Lỗi khi tải dữ liệu!');
        }
    });
}



function openAddModal() {
    const $modal = $('#exampleModal'); // Lấy modal bằng jQuery

    $modal.find('.modal-title').text('Thêm phòng ban'); // Đặt tiêu đề modal
    $modal.find('input.category_name').val(''); // Xóa giá trị cũ
    $modal.find('input.category_id').val(''); // Không có ID khi thêm
    $modal.find('input.action').val(0); // Đặt action = 0 (thêm)
    $modal.modal('show'); // Hiển thị modal
}

// Mở modal để cập nhật
function openEditModal(categoryId, categoryName, enable) {
    const $modal = $('#exampleModal'); // Lấy modal bằng jQuery
    $modal.find('.modal-title').text('Cập nhật danh mục'); // Đặt tiêu đề modal
    $modal.find('input.category_name').val(categoryName); // Điền tên danh mục
    $modal.find('input.category_id').val(categoryId); // Gắn ID
    if(enable == 1)
    {
        $('.toggle').addClass('active')
        $('.toggle-hidden').find('.enableHidden').val(1);
        $('.toggle-hidden').find('.text').text('Công khai')
    }
    else
    {
        $('.toggle').removeClass('active')
        $('.toggle-hidden').find('.enableHidden').val(0);
        $('.toggle-hidden').find('.text').text('Riêng tư')
    }
    $modal.find('input.action').val(1); // Đặt action = 1 (cập nhật) 
    $modal.modal('show'); // Hiển thị modal
    
}

function openAddPostModal() {
    const $modal = $('#exampleModal'); // Lấy modal bằng jQuery

    // Đặt lại các giá trị trong modal để chuẩn bị thêm mới
    $modal.find('.modal-title').text('Thêm bài viết'); // Đặt tiêu đề
    $modal.find('input.chapterName').val(''); // Xóa giá trị tên bài viết cũ
    $modal.find('#image-preview').html(''); // Xóa preview hình ảnh
    $modal.find('#files-list').html(''); // Xóa danh sách file

    // Đảm bảo form trỏ tới đường dẫn thêm bài viết


    // Hiển thị modal
    $modal.modal('show');
}

function openAddGVModal()
{
    const $modal = $('#exampleModal')
    $modal.find('.modal-title').text('Thêm thông tin giáo viên')
    $modal.find('input.chapterName').val('')
    $modal.find('.role1').val('')
    $modal.find('.role2').val('')
    $modal.find('.chuyenmon').val('')
    $modal.find('.namsinh').val('')
    $modal.find('#image-preview').html(''); 
    $modal.modal('show');
}

function openEditGVModal(gv_id, name, role1, role2, date, chuyenmon, sex, bac, enable, image_file) {
    // Lấy các input field trong form
    const $postInput = $('#exampleModal .post-id');
    const $actionInput = $('#exampleModal .action');
    const $nameInput = $('#exampleModal .chapterName');
    const $role1Input = $('#exampleModal .role1');
    const $role2Input = $('#exampleModal .role2');
    const $dateInput = $('#exampleModal .namsinh');
    const $chuyenmonInput = $('#exampleModal .chuyenmon');
    const $sexSelect = $('#exampleModal #sex');
    const $bacSelect = $('#exampleModal #bac');
    const $enableInput = $('#exampleModal .enableHidden');
    const $imageInput = $('#exampleModal #topic-image');
  
    // Điền các giá trị vào các input field
    $postInput.val(gv_id)
    $actionInput.val(1)
    $nameInput.val(name);
    $role1Input.val(role1);
    $role2Input.val(role2);
    $dateInput.val(date);
    $chuyenmonInput.val(chuyenmon);
    $sexSelect.val(sex);
    $bacSelect.val(bac);
    $enableInput.val(enable);
  
    // Xử lý hình ảnh
    // Ví dụ: hiển thị hình ảnh trong preview
    const imagePreview = $('#exampleModal #image-preview');
    if (image_file) {
      imagePreview.html(`<img src="${image_file}" alt="Preview" class="img-fluid">`);
    } else {
      imagePreview.html('');
    }

    const $modal = $('#exampleModal')
    $modal.modal('show')
  }

$('#topic-files').on('change', function() {
    if (this.files.length > 0) {
        // Nếu người dùng đã chọn file mới, reset file cũ
        $('#files-list').html('');
        $('#existing-files').val('');  // Xóa giá trị của các file cũ trong hidden input
    } else {
        // Nếu không chọn file mới, giữ lại các file cũ
        let existingFiles = JSON.parse($('#existing-files').val());
        let fileList = '';

        existingFiles.forEach(function(file) {
            fileList += `<a href="${file.url}" target="_blank">${file.name}</a><br>`;
        });

        $('#files-list').html(fileList);  // Hiển thị lại danh sách file cũ
    }
});



// document.querySelector('#course').addEventListener('submit', function (event) {
//     // Kiểm tra giá trị của trường select "Lớp"
//     const grade = document.querySelector('#grade').value;
//     if (grade === "0") {
//         event.preventDefault() // Ngăn chặn việc submit form
//         const gradeError = document.querySelector('#gradeError');
//         gradeError.classList.remove('d-none');
//         return false;
//     }
//     else{
//         const gradeError = document.querySelector('#gradeError');
//         gradeError.classList.add('d-none')
//     }

//     // Kiểm tra giá trị của trường select "Môn"
//     const subject = document.querySelector('#subject').value;
//     if (subject === "#") {
//         event.preventDefault(); // Ngăn chặn việc submit form
//         const subjectError = document.querySelector('#subjectError');
//         subjectError.classList.remove('d-none');
//         return false;
//     }
//     else{
//         const subjectError = document.querySelector('#subjectError');
//         subjectError.classList.add('d-none');
//     }
// });
// Tránh xung đột bằng cách sử dụng noConflict()

// Bây giờ bạn có thể sử dụng "jq" thay vì "$" để thực hiện các phương thức của jQuery

$(document).ready(function () {

    $('#menu-btn').click(function () {
        $('#menu').toggleClass('active')
    });

    $('.toggle-button').on('click', function () {

        $(this).closest('.toggle').toggleClass('active')

        const textElement = $(this).closest('.toggle-hidden').find('.text');
        const enableValue = $(this).closest('.toggle-hidden').find('.enableHidden');
        if ($(this).closest('.toggle').hasClass('active')) {
            textElement.text('Công khai');
            enableValue.val(1)
        } else {
            textElement.text('Riêng tư');
            enableValue.val(0)
        }
    })
    // $('.toggle-button').click(function () {
    //     $('.toggle').toggleClass('active')

    //     const textElement = $('.text');
    //     if ($('.toggle').hasClass('active')) {
    //         textElement.text('Công khai');
    //         document.querySelector('.enableHidden').value = 1
    //     } else {
    //         textElement.text('Riêng tư');
    //         document.querySelector('.enableHidden').value = 0
    //     }
    // });

    $('.role-select').on('change', function () {

        var role = $(this).val();
        const accountId = $(this).data('account-id');
        $.ajax({
            url: '/adminpage/get_role/',
            type: 'GET',
            data: {
                'account_id': accountId,
                'role': role,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function (response) {
                location.reload();
            },

            error: function (xhr, status, error) {
                console.log(error);
            }
        })
    });

    $('#course').submit(function (event) {
        event.preventDefault(); // Ngăn chặn gửi biểu mẫu ngay lập tức
        const action = $(this).find('.action').val()

        if(action == 0)
        {
            $('.modal-text').text('Đã thêm dữ liệu.');
        }
        else{
            $('.modal-text').text('Đã cập nhật dữ liệu.');
        }

        // Ẩn modal hiện tại
        $('#exampleModal').modal('hide');
    
        // Hiển thị modal thông báo thành công
        
        $('#successModal').modal('show');
    
        // Khi người dùng đóng modal thành công, gửi biểu mẫu
        $('#closeSuccessModalButton').click(function () {
            $('#course')[0].submit();
        });
    });

    







    $('.btncourse').click(function () {
        // Thực hiện các hành động cụ thể khi modal được đóng

        $('#course').find('.course_name').val(null)
        CKEDITOR.instances.editor1.setData(null);
        $('#course').find('.picture').attr('src', '')
        $('#course').find('.toggle').addClass('active')
        $('#course').find('.toggle-hidden .text').text('Công khai')
        $('#course').find('.enableHidden').val(1)
        $('#course').find('.enableHidden2').val(1)
        $('#course').find('.action').val(0)
        $('#course').find('.courseHidden').val(null)
    });


    $('#courseUpdate').submit(function (event) {
        event.preventDefault();

        const course_name = $('.course_name').val()
        const grade_id = $('#grade').val()
        const subject_id = $('#subject').val()
        const course_id = $('.courseHidden').val()
        const enableHidden = $('.enableHidden').val()

        $.ajax({
            url: '/adminpage/get_course_update/',
            type: 'GET',
            data: {
                'courseName': course_name,
                'grade_id': grade_id,
                'subject_id': subject_id,
                'course_id': course_id,
                'course_enable': enableHidden,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.name === false) {
                    $('#courseNameError').removeClass('d-none')
                    return false;

                }
                else if (response.submit === true) {
                    $('#exampleModal').modal('hide')
                    //$('.modal-text').text('Đã thêm dữ liệu.')
                    $('#successModal').modal('show');
                    $('#closeSuccessModalButton').click(function () {
                        $('#courseUpdate')[0].submit();
                    })
                }



            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    })

    $('#activity').submit(function (event) {
        // Ngăn chặn hành động mặc định khi submit form
        event.preventDefault();

        // Lấy giá trị của trường select "Khoá học"
        const chapter = $('#activityType').val();
        console.log(chapter);

        // Kiểm tra giá trị của trường select "Khoá học"
        if (chapter === "#") {
            // Hiển thị thông báo lỗi
            $('#activityTypeError').removeClass('d-none');
        } else {
            // Ẩn thông báo lỗi (nếu có)
            $('#activityTypeError').addClass('d-none');

            // Submit form nếu giá trị hợp lệ
            $('#activity')[0].submit();
        }
    });

    $('#chapter').submit(function (event) {
        event.preventDefault()
        var chapterName = $('.chapterName').val();
        var stt = $('.tt').val();
        var course_id = $('.courseHidden').val();
        if (chapterName != null) {
            $.ajax({
                url: '/adminpage/get_chapter/',
                type: 'GET',
                data: {
                    'chapterName': chapterName,
                    'stt': stt,
                    'course_id': course_id,
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {
                    if (response.name === false) {
                        $('#chapterNameError').removeClass('d-none')
                        return false;

                    }
                    else if (response.order === false) {
                        $('#chapterOrderError').removeClass('d-none')
                        return false

                    }
                    else if (response.submit === true) {
                        $('#chapter')[0].submit();
                    }



                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        }
    });


    $('#chapterUpdate').submit(function (event) {
        event.preventDefault();
        var chapterName = $('.chapterNameUpdate').val();
        var course_id = $('.courseHidden').val();
        var stt = $('.chapterOrderUpdate').val();
        var chapter_id = $('.chapterHidden').val();
        var enableHidden = $('.enableHidden').val();
        if (chapterName != null) {
            $.ajax({
                url: '/adminpage/get_chapter_update/',
                type: 'GET',
                data: {
                    'chapterName': chapterName,
                    'stt': stt,
                    'course_id': course_id,
                    'chapter_id': chapter_id,
                    'enableHidden': enableHidden,
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {
                    if (response.name === false) {
                        $('#chapterNameError').removeClass('d-none')
                        return false;

                    }
                    else if (response.order === false && response.order !== null) {
                        $('#chapterOrderError').removeClass('d-none')
                        return false

                    }
                    else if (response.submit === true) {
                        $('#successModal').modal('show');
                        $('#closeSuccessModalButton').click(function () {
                            $('#chapterUpdate')[0].submit();
                        })

                    }


                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        }
    })

    $('#lesson').submit(function (event) {
        event.preventDefault();
        var lessonName = $('.lessonName').val()
        var lessonOrder = $('.lessonOrder').val()
        var chapter_id = $('.chapterHidden').val()
        if (lessonName != null) {
            $.ajax({
                url: '/adminpage/get_lesson/',
                type: 'GET',
                data: {
                    'lessonName': lessonName,
                    'lessonOrder': lessonOrder,
                    'chapter_id': chapter_id,
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {

                    if (response.name === false) {
                        $('#lessonNameError').removeClass('d-none')
                        return false;

                    }
                    else if (response.order === false) {
                        $('#lessonOrderError').removeClass('d-none')
                        return false

                    }
                    else if (response.submit === true) {
                        $('#exampleModal').modal('hide')
                        $('.modal-text').text('Đã thêm dữ liệu!')
                        $('#successModal').modal('show');
                        $('#closeSuccessModalButton').click(function () {
                            $('#lesson')[0].submit();
                        })

                    }


                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        }
    })


    $('#lessonUpdate').submit(function (event) {
        event.preventDefault();
        var lessonName = $('.lessonName').val()
        var lessonOrder = $('.lessonOrder').val()
        var chapter_id = $('.chapterHidden').val()
        var enableHidden = $('.enableHidden').val();
        var lesson_id = $('.lessonHidden').val();
        if (lessonName != null) {
            $.ajax({
                url: '/adminpage/get_lesson_update/',
                type: 'GET',
                data: {
                    'lessonName': lessonName,
                    'lessonOrder': lessonOrder,
                    'chapter_id': chapter_id,
                    'enableHidden': enableHidden,
                    'lesson_id': lesson_id,
                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {

                    if (response.name === false) {
                        $('#lessonNameError').removeClass('d-none')
                        return false;

                    }
                    else if (response.order === false) {
                        $('#lessonOrderError').removeClass('d-none')
                        return false

                    }
                    else if (response.submit === true) {
                        $('#exampleModal').modal('hide')
                        //$('.modal-text').text('Đã thêm dữ liệu!')
                        $('#successModal').modal('show');
                        $('#closeSuccessModalButton').click(function () {
                            $('#lessonUpdate')[0].submit();
                        })

                    }


                },
                error: function (xhr, status, error) {
                    console.log(error);
                }
            });
        }
    })

    $('#activityDetail').submit(function (event) {
        event.preventDefault();
        var activityName = $('.activityName').val()
        var activityOrder = $('.activityOrder').val()
        var enableHidden = $(this).find('.enableHidden').val();
        var enableHidden2 = $('.enableHidden2').val();
        var course_id = $('.courseHidden').val()
        var activityType = $('#activityType').val()
        console.log(enableHidden)
        console.log(enableHidden2)
        if (activityType !== '0') {
            if (enableHidden == enableHidden2 || enableHidden === null) {
                $.ajax({
                    url: '/adminpage/get_activity/',
                    type: 'GET',
                    data: {
                        'activityName': activityName,
                        'activityOrder': activityOrder,
                        'course_id': course_id,
                        'activityType': activityType,
                        csrfmiddlewaretoken: '{{ csrf_token }}',
                    },
                    success: function (response) {

                        if (response.name === false) {
                            $('#activityNameError').removeClass('d-none')
                            return false;

                        }
                        else if (response.order === false) {
                            $('#activityOrderError').removeClass('d-none')
                            return false

                        }
                        else if (response.submit === true) {
                            $('#exampleModal').modal('hide')
                            $('.modal-text').text('Đã thêm dữ liệu!')
                            $('#successModal').modal('show');
                            $('#closeSuccessModalButton').click(function () {
                                $('#activityDetail')[0].submit();
                            })

                        }


                    },
                    error: function (xhr, status, error) {
                        console.log(error);
                    }
                });
            }
            else if (enableHidden !== enableHidden2) {
                $('#exampleModal').modal('hide')
                $('.modal-text').text('Dữ liệu đã được cập nhập!')
                $('#successModal').modal('show');
                $('#closeSuccessModalButton').click(function () {
                    $('#activityDetail')[0].submit();
                })
            }
        }
        else {
            $('#activityTypeError').removeClass('d-none')
            return false
        }
    })

    $('#posttype').submit(function (event) {
        event.preventDefault();
        var posttypeName = $('.posttype_name').val();

        $.ajax({
            url: '/adminpage/get_posttype/',
            type: 'GET',
            data: {
                'posttypeName': posttypeName,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function (response) {

                if (response.name === false) {
                    $('#posttypeNameError').removeClass('d-none')
                    return false;

                }
                else if (response.submit === true) {
                    $('#exampleModal').modal('hide')
                    $('.modal-text').text('Đã thêm dữ liệu!')
                    $('#successModal').modal('show');
                    $('#closeSuccessModalButton').click(function () {
                        $('#posttype')[0].submit();
                    })

                }


            },
            error: function (xhr, status, error) {
                console.log(error);
            }
        });
    })

    $('.approved').click(function () {
        var action = $(this).data('action')
        var postId = $(this).data('postid')
        $.ajax({
            url: '/adminpage/submit_approved/',
            type: 'GET',
            data: {
                'post_id': postId,
                'action': action,
                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function (response) {
                location.reload();
            },

            error: function (xhr, status, error) {
                console.log(error);
            }
        })
    })

    $('.comment-trigger').on('click', function () {
        var commentId = $(this).data('commentid');
        $('#first-reply-' + commentId).toggleClass('d-none');
    });

    $('.delete').on('click', function () {
        var commentId = $(this).data('commentid')
        $('#successModal').modal('show');
        $('#successModalButton').click(function () {
            $.ajax({
                url: '/adminpage/delete_comment/',
                type: 'GET',
                data: {
                    'comment_id': commentId,

                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {
                    location.reload();
                },

                error: function (xhr, status, error) {
                    console.log(error);
                }
            })
        })
    })

    $('.change-active').on('click', function () {
        var post_id = $(this).data('postid')
        var action = $(this).data('action')
        if (action === 0) {
            $('.modal-text').html('Bạn có chắc muốn vô hiệu bài viết này?')
        }
        else if (action === 1) {
            $('.modal-text').html('Bạn có chắc muốn bật bài viết này?')
        }
        $('#successModal').modal('show');
        $('#successModalButton').click(function () {
            $.ajax({
                url: '/adminpage/change_active/',
                type: 'GET',
                data: {
                    'post_id': post_id,
                    'action': action,

                    csrfmiddlewaretoken: '{{ csrf_token }}',
                },
                success: function (response) {
                    location.reload();
                },

                error: function (xhr, status, error) {
                    console.log(error);
                }
            })
        })

    })

    $('#activity1').submit(function (event) {
        event.preventDefault()

        const data = $('.dataHidden').val()
        const type_id = $('.type-id').val()
        const name = $(this).find('.Name').val()
        const activity_id = $('.activityHidden').val()
        if (!data) {
            if (type_id === '1') {
                const order = $(this).find('.order').val()
                $.ajax({
                    url: '/adminpage/check_activity/',
                    type: 'GET',
                    data: {
                        'type_id': type_id,
                        'name': name,
                        'activity_id': activity_id,
                        'order': order,
                        'action': 0,
                        csrfmiddlewaretoken: '{{ csrf_token }}',
                    },
                    success: function (response) {

                        if (response.name === false) {
                            $('#nameError').removeClass('d-none')
                            return false;

                        }
                        else if (response.order === false) {
                            $('#orderError').removeClass('d-none')
                            return false
                        }
                        else if (response.submit === true) {
                            $('#exampleModal').modal('hide')
                            $('.modal-text').text('Đã thêm dữ liệu!')
                            $('#successModal').modal('show');
                            $('#closeSuccessModalButton').click(function () {
                                $('#activity1')[0].submit();
                            })

                        }


                    },
                    error: function (xhr, status, error) {
                        console.log(error);
                    }
                });
            }
            else {
                var fileInput = $('#topic-file')
                var file = fileInput[0].files[0]
                var fileType = file.type;
                if (!fileType.startsWith('image/')) {
                    $('#uploadError').removeClass('d-none')
                    $('#uploadError').html("file không được hỗ trợ!")
                    return;
                }
                $.ajax({
                    url: '/adminpage/check_activity/',
                    type: 'GET',
                    data: {
                        'type_id': type_id,
                        'name': name,
                        'activity_id': activity_id,
                        'action': 0,
                        csrfmiddlewaretoken: '{{ csrf_token }}',
                    },
                    success: function (response) {

                        if (response.name === false) {
                            $('#nameError').removeClass('d-none')
                            return false;

                        }
                        else if (response.submit === true) {
                            $('#exampleModal').modal('hide')
                            $('.modal-text').text('Đã thêm dữ liệu!')
                            $('#successModal').modal('show');
                            $('#closeSuccessModalButton').click(function () {
                                $('#activity1')[0].submit();
                            })

                        }


                    },
                    error: function (xhr, status, error) {
                        console.log(error);
                    }
                });

            }
        }
        else {
            const enableValue = $(this).find('.toggle-hidden').find('.enableHidden').val()
            const enableValue2 = $(this).find('.toggle-hidden').find('.enableHidden2').val()
            if (enableValue === enableValue2) {
                if (type_id === '1') {
                    const order = $(this).find('.order').val()

                    $.ajax({
                        url: '/adminpage/check_activity/',
                        type: 'GET',
                        data: {
                            'type_id': type_id,
                            'name': name,
                            'activity_id': activity_id,
                            'order': order,
                            'action': 1,
                            'data': data,
                            csrfmiddlewaretoken: '{{ csrf_token }}',
                        },
                        success: function (response) {

                            if (response.name) {
                                $('#nameError').removeClass('d-none')
                                return false;

                            }
                            else if (response.order) {
                                $('#orderError').removeClass('d-none')
                                return false
                            }
                            else if (response.submit) {
                                $('#exampleModal').modal('hide')
                                $('.modal-text').text('Đã cập nhật dữ liệu!')
                                $('#successModal').modal('show');
                                $('#closeSuccessModalButton').click(function () {
                                    $('#activity1')[0].submit();
                                })

                            }


                        },
                        error: function (xhr, status, error) {
                            console.log(error);
                        }
                    });
                }
                else {
                    var fileInput = $('#topic-file')
                    var file = fileInput[0].files[0]
                    if (file) {
                        var fileType = file.type;

                        if (!fileType.startsWith('image/')) {
                            $('#uploadError').removeClass('d-none')
                            $('#uploadError').html("file không được hỗ trợ!")
                            return;
                        }
                    }

                    $.ajax({
                        url: '/adminpage/check_activity/',
                        type: 'GET',
                        data: {
                            'type_id': type_id,
                            'name': name,
                            'activity_id': activity_id,
                            'action': 1,
                            'data': data,
                            csrfmiddlewaretoken: '{{ csrf_token }}',
                        },
                        success: function (response) {

                            if (response.name === false) {
                                $('#nameError').removeClass('d-none')
                                return false;

                            }
                            else if (response.submit === true) {
                                $('#exampleModal').modal('hide')
                                $('.modal-text').text('Đã cập nhật dữ liệu!')
                                $('#successModal').modal('show');
                                $('#closeSuccessModalButton').click(function () {
                                    $('#activity1')[0].submit();

                                })

                            }


                        },
                        error: function (xhr, status, error) {
                            console.log(error);
                        }
                    });

                }
            }
            else {
                $('#exampleModal').modal('hide')
                $('.modal-text').text('Đã cập nhật dữ liệu!')
                $('#successModal').modal('show');
                $('#closeSuccessModalButton').click(function () {
                    $('#activity1')[0].submit();

                })
            }

        }



    })

    $('.update').on('click', function () {

        const id = $(this).data('id')
        const type_id = $('.type-id').val()
        console.log('a')

        $.ajax({
            url: '/adminpage/get_data_activity/',
            type: 'GET',
            data: {
                'id': id,
                'type_id': type_id,

                csrfmiddlewaretoken: '{{ csrf_token }}',
            },
            success: function (response) {

                if (response.theory) {
                    $('.dataHidden').val(response.theory.theory_id)
                    $('.Name').val(response.theory.theory_name)
                    $('.order').val(response.theory.theory_order)
                    $('.link').val(response.theory.theory_hyperlink)
                    $('#exampleModalLabel').html('Cập nhật lý thuyết')
                    $('.btn-update').html("Cập nhật")
                    if (response.theory.theory_enable) {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').addClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Công khai")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(1)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(1)
                    }
                    else {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').removeClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Riêng tư")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(0)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(0)
                    }
                }
                else if (response.game) {
                    $('#exampleModalLabel').html('Cập nhật trò chơi')
                    $('.btn-update').html("Cập nhật")
                    $('.dataHidden').val(response.game.game_id)
                    $('.Name').val(response.game.game_name)
                    $('.link').val(response.game.game_hyperlink)
                    CKEDITOR.instances.editor1.setData(response.game.game_content);
                    const fileUrl = response.game.game_picture;

                    const file = new File([], fileUrl.split('/').pop(), {
                        type: 'image/jpeg'
                    });

                    const fileInput = $('#topic-file');
                    fileInput.files = [file];
                    $('.picture').attr('src', response.game.game_picture);
                    if (response.game.game_enable) {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').addClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Công khai")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(1)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(1)
                    }
                    else {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').removeClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Riêng tư")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(0)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(0)
                    }



                }
                else if (response.simulaiton) {
                    $('#exampleModalLabel').html('Cập nhật mô phỏng')
                    $('.btn-update').html("Cập nhật")
                    $('.dataHidden').val(response.simulaiton.simulation_id)
                    $('.Name').val(response.simulaiton.simulation_name)
                    $('.link').val(response.simulaiton.simulation_hyperlink)
                    CKEDITOR.instances.editor1.setData(response.simulaiton.simulation_content);
                    const fileUrl = response.simulaiton.simulation_picture;

                    const file = new File([], fileUrl.split('/').pop(), {
                        type: 'image/jpeg'
                    });

                    const fileInput = $('#topic-file');
                    fileInput.files = [file];
                    $('.picture').attr('src', response.simulaiton.simulation_picture);
                    if (response.simulaiton.simulation_enable) {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').addClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Công khai")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(1)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(1)
                    }
                    else {
                        $('#activity1').find('.toggle-hidden').removeClass('d-none')
                        $('#activity1').find('.toggle-hidden').find('.toggle').removeClass('active')
                        $('#activity1').find('.toggle-hidden').find('text').text("Riêng tư")
                        $('#activity1').find('.toggle-hidden').find('.enableHidden').val(0)
                        $('#activity1').find('.toggle-hidden').find('.enableHidden2').val(0)
                    }
                }
                $('#exampleModal').modal('show')
            },

            error: function (xhr, status, error) {
                console.log(error);
            }
        })

        $('#topic-file').change(function (e) {
            const file = e.target.files[0];

            // Kiểm tra file phải là hình ảnh
            if (!file.type.startsWith('image/')) {
                return;
            }

            // Tạo đối tượng URL từ file hình
            const url = URL.createObjectURL(file);

            // Set lại src của img
            $('.picture').attr('src', url);

            // Xử lý khi đóng trang  
            window.addEventListener('beforeunload', () => {
                URL.revokeObjectURL(url);
            })
        })


    })

    $('.btn-add').click(function () {

        $('.dataHidden').val(null)
        $('.Name').val(null)
        $('.order').val(null)
        $('.link').val(null)
        $('.picture').attr('src', null);
        $('#topic-file').val(null)
        $('#activity1').find('.toggle-hidden').removeClass('d-none')
        const type_id = $('.type-id').val()

        if (type_id == '1') {
            $('#exampleModalLabel').html('Thêm lý thuyết')
            $('.btn-update').html("Thêm")
        }
        else if (type_id == '2') {
            CKEDITOR.instances.editor1.setData(null);
            $('#exampleModalLabel').html('Thêm trò chơi')
            $('.btn-update').html("Thêm")
        }
        else {
            CKEDITOR.instances.editor1.setData(null);
            $('#exampleModalLabel').html('Thêm mô phỏng')
            $('.btn-update').html("Thêm")
        }

    })



    // Các phần khác của mã jQuery sử dụng "jq" thay vì "$" tại đây
});

if (document.querySelector('.activityOrder').value < 1) {
    document.querySelector('.activityOrder').value = 1
}















