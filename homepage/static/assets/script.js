// $('.navbar').on('mouseenter', function() {
//     $(this).css('background-color', 'rgba(255,255,255,0.8)'); // Độ đậm hơn khi người dùng di chuột qua
// }).on('mouseleave', function() {
//     $(this).css('background-color', 'rgba(255,255,255,0.5)'); // Trở về độ mờ ban đầu khi người dùng rời chuột
// });


function reloadWithPBID() {
    const selectElement = document.getElementById('mySelect');
    const selectedPBID = selectElement.value;

    // Điều hướng đến URL mới dạng /cctc/pb_id/
    window.location.href = `/cctc/${selectedPBID}/`;
  }


  function openAddPostModal() {
    const $modal = $('#exampleModal'); // Lấy modal bằng jQuery

    // Đặt lại các giá trị trong modal để chuẩn bị thêm mới
    // $modal.find('.modal-title').text('Thêm bài viết'); // Đặt tiêu đề
    // $modal.find('input.chapterName').val(''); // Xóa giá trị tên bài viết cũ
    // $modal.find('#image-preview').html(''); // Xóa preview hình ảnh
    // $modal.find('#files-list').html(''); // Xóa danh sách file

    // Đảm bảo form trỏ tới đường dẫn thêm bài viết


    // Hiển thị modal
    $modal.modal('show');
}

