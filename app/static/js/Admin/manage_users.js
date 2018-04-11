//
// Links
//

$('#admin-users-link').on('click', function () {
    $('#user-operation').val('admin');
    $('#user-management').submit();
});

$('#delete-users-link').on('click', function () {
    $('#user-operation').val('delete');
    $('#user-management').submit();
});

$('#disable-users-link').on('click', function () {
    $('#user-operation').val('disable');
    $('#user-management').submit();
});