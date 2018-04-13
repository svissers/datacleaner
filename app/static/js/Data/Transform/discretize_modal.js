$('#discretize-radio-1').on('click', function () {
    $('#amount-dist').prop('required', true);
    $('#amount-freq').prop('required', false);
    $('#custom-edges').prop('required', false);
});

$('#discretize-radio-2').on('click', function () {
    $('#amount-dist').prop('required', false);
    $('#amount-freq').prop('required', true);
    $('#custom-edges').prop('required', false);
});

$('#discretize-radio-3').on('click', function () {
    $('#amount-dist').prop('required', false);
    $('#amount-freq').prop('required', false);
    $('#custom-edges').prop('required', true);
});