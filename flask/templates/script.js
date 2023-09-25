// JavaScript to handle form submission
$(document).ready(function () {
    $('#filter-form').submit(function (e) {
        e.preventDefault();
        // Get min_price and max_price values
        var minPrice = $('#min_price').val();
        var maxPrice = $('#max_price').val();
        // Send an AJAX request to update the filtered data
        $.ajax({
            url: '/',
            type: 'GET',
            data: {
                min_price: minPrice,
                max_price: maxPrice
            },
            success: function (data) {
                // Replace the entire table container with the updated data
                $('#table-container').html(data);
            }
        });
    });
});
