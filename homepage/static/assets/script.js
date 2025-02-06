$('.navbar').on('mouseenter', function() {
    $(this).css('background-color', 'rgba(255,255,255,0.8)'); // Độ đậm hơn khi người dùng di chuột qua
}).on('mouseleave', function() {
    $(this).css('background-color', 'rgba(255,255,255,0.5)'); // Trở về độ mờ ban đầu khi người dùng rời chuột
});


function reloadWithPBID() {
    const selectElement = document.getElementById('mySelect');
    const selectedPBID = selectElement.value;

    // Điều hướng đến URL mới dạng /cctc/pb_id/
    window.location.href = `/cctc/${selectedPBID}/`;
  }


