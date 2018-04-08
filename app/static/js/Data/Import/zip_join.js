var columns = {};
var counter = 0;
// SOURCE: https://stackoverflow.com/questions/24816/escaping-html-strings-with-jquery
var entityMap = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;'
};
function escapeHtml (string) {
  return String(string).replace(/[&<>"'`=\/]/g, function (s) {
    return entityMap[s];
  });
}
$.get('/data/upload/extract_columns', function( data ) {
    columns = data;
});
$(document).on('change', '.file-select', function () {
    var select_field = $(this);
    var col = null;
    if (select_field.attr('id') === 'file-left'){
        col = $('#column-left');
    }
    else if (select_field.attr('id') === 'file-right'){
        col = $('#column-right');
    }
    col.empty();
    var cols = columns[select_field.val()];
    var arrayLength = cols.length;
    for (var i = 0; i < arrayLength; ++i) {
        col.append($('<option></option>').text(cols[i]));
    }
});
$(document).on('click', '.add-join-btn', function () {
    var file_left = $('#file-left').val();
    var column_left = $('#column-left').val();
    var join_type = $('#join-type').val();
    var file_right = $('#file-right').val();
    var column_right = $('#column-right').val();
    var join_name = $('#join-name').val();
    var join_description = $('#join-description').val();
    if ( column_left != null && column_right != null
        && join_name !== '' && join_description !== ''
    ) {
        $('#join_table').find('tbody').prepend(
        '<tr id="join-row' + counter + '">' +
        '<td><input class="form-control" name="file-left' + counter + '" type="text" value="' + escapeHtml(file_left) + '" ' +
        'placeholder="' + escapeHtml(file_left) + '" readonly required><hr/>' +
        '<input class="form-control" name="column-left' + counter + '" type="text" value="' + escapeHtml(column_left) + '" ' +
        'placeholder="' + escapeHtml(column_left) + '" readonly required></td>' +
        '<td><input class="form-control" name="join-type' + counter + '" type="text" value="' + escapeHtml(join_type) + '" ' +
        'placeholder="' + escapeHtml(join_type) + '" readonly required></td>' +
        '<td><input class="form-control" name="file-right' + counter + '" type="text" value="' + escapeHtml(file_right) + '" ' +
        'placeholder="' + escapeHtml(file_right) + '" readonly required><hr/>' +
        '<input class="form-control" name="column-right' + counter + '" type="text" value="' + escapeHtml(column_right) + '" ' +
        'placeholder="' + escapeHtml(column_right) + '" readonly required></td>' +
        '<td><input class="form-control" name="join-name' + counter + '" type="text" value="' + escapeHtml(join_name) + '" ' +
        'placeholder="' + escapeHtml(join_name) + '" readonly required></td>' +
        '<td><input class="form-control" name="join-description' + counter + '" type="text" value="' + escapeHtml(join_description) + '" ' +
        'placeholder="' + escapeHtml(join_description) + '" readonly required></td>' +
        '<td><button type="button" class="btn btn-warning btn-block remove-join-btn"><i class="fas fa-minus"></i></button></td>' +
        '</tr>'
    );
    ++counter;
    }
});
$(document).on('click', '.remove-join-btn', function () {
    $(this).closest ('tr').remove ();
});