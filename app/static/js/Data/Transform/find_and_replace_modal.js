$('.far-match-radio').on('click', function () {
    var radios = $('.far-replace-radio');
    if ($(this).val() === 'substring-match') {
        radios.prop('required', true);
        radios.prop('disabled', false);
    }
    else {
        radios.prop('required', false);
        radios.prop('disabled', true);
        radios.prop('checked', false);
    }
})

$('#far_column_select').on('change', function () {
    var radios = $('.far-text-type-only')
    var type = $('#far_column_select option:selected').data('type')
    if (type === 'BIGINT' || type === 'INTEGER' || type === 'DOUBLE PRECISION'){
        radios.prop('disabled', true);
        radios.prop('checked', false);
    }
    else{
        radios.prop('disabled', false);
    }
})