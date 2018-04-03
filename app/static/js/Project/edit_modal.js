$('#edit-project-modal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var project_id = button.data('projectid');
  var project_title = button.data('title');
  var project_desc = button.data('description');
    $('#edit-hidden-id').val(project_id);
    $('#edit-title').val(project_title);
    $('#edit-desc').val(project_desc);
})