$('#extract-from-select').on('change', function () {
    var insert_select = $('#extract-part-select');
    var col_type = $('#extract-from-select option:selected').data('type');
    insert_select.empty();
    var from_time = ['Hours', 'Minutes', 'Seconds'];
    var from_time_val = ['hour', 'minute', 'second'];
    var from_date = ['Year', 'Month', 'Quarter', 'Week of the year', 'Day of the year' , 'Day of the month', 'Day of the week'];
    var from_date_val = ['year', 'month', 'quarter', 'week', 'doy' , 'day', 'isodow'];
    if (col_type === 'TIMESTAMP'){
        insert_select.append($('<option></option>').val('date').text('Date'));
        insert_select.append($('<option></option>').val('time').text('Time'));
        var arrayLength2 = from_time.length;
        for (var i = 0; i < arrayLength2; ++i) {
            insert_select.append($('<option></option>').val(from_time_val[i]).text(from_time[i]));
        }
    }
    if (col_type === 'DATE' || col_type === 'TIMESTAMP'){
        var arrayLength1 = from_date.length;
        for (var i = 0; i < arrayLength1; ++i) {
            insert_select.append($('<option></option>').val(from_date_val[i]).text(from_date[i]));
        }
    }
});