var counter = 1;
$(document).on('click', '.add-delete-btn', function () {
    var column = $('#column').val();
    var operator = $('#operator').val();
    var condition = $('#condition').val();
    if (condition !== '') {
        $('#delete_table').find('tbody tr:last').before(
            '<tr>' +
            '<td><input class="form-control" name="column' + counter + '" type="text" value="' + column + '" readonly></td>' +
            '<td><input class="form-control" name="operator' + counter + '" type="text" value="' + operator + '" readonly></td>' +
            '<td><input class="form-control" name="condition' + counter + '" type="text" value="' + condition + '" readonly></td>' +
            '<td>' +
            '<select class="form-control" name="logical' + counter + '">\n' +
            '<option>AND</option><option>OR</option>' +
            '</select>' +
            '<td>' +
            '<button type="button" class="btn btn-warning btn-block remove-delete-btn">' +
            '<i class="fas fa-minus"></i>' +
            '</button>' +
            '</td>' +
            '</tr>'
        );
        ++counter;
    }
});
$(document).on('click', '.remove-delete-btn', function () {
    $(this).closest ('tr').remove ();
});