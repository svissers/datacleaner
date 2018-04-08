$(document).on('show.bs.collapse hide.bs.collapse', '.sidebar-collapse', function () {
    var id = $(this).attr('id');
    var toggle_id = id.substring(0, id.lastIndexOf('-')) + '-toggle';
    var carret = $('#'+toggle_id);

    if (carret.hasClass('fa-caret-right')) {
        carret.removeClass('fa-caret-right');
        carret.addClass('fa-caret-down');
    }
    else {
        carret.removeClass('fa-caret-down');
        carret.addClass('fa-caret-right');
    }
});