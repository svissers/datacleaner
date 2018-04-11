function update_columns(id, data) {
    var col = null;
    if (id === 'file-left'){
        col = $('#column-left');
    }
    else if (id === 'file-right'){
        col = $('#column-right');
    }
    col.empty();
    var arrayLength = data.length;
    console.log(arrayLength);
    for (var i = 0; i < arrayLength; ++i) {
        col.append($('<option></option>').text(data[i]));
    }
}

$(document).on('change', '.file-select', function () {
    var dataset_id = $(this).val();
    var field = $(this).attr('id');
    $.get('/data/view/get_columns', {dataset_id: dataset_id}, function (data) {
        update_columns(field, data);
    })
} );
