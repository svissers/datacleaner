$('#edit-dataset-modal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var dataset_id = button.data('projectid');
  var dataset_title = button.data('title');
  var dataset_desc = button.data('description');
    $('#edit-hidden-id').val(dataset_id);
    $('#edit-title').val(dataset_title);
    $('#edit-desc').val(dataset_desc);
})