$('#share-project-modal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget);
  var project_id = button.data('projectid');
    $('#share-hidden-id').val(project_id);
})

$(document).ready(function () {
    localStorage.clear();
    // Constructs the suggestion engine
    var users = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        // The url points to a json file that contains an array of country names
        prefetch: "/user/autocomplete"
    });

    // Initializing the typeahead with remote dataset without highlighting
    $('.typeahead').typeahead(null, {
        name: 'users',
        source: users,
        limit: 5, /* Specify max number of suggestions to be displayed */
        hint: false,
        highlight: false, /* Enable substring highlighting */
        minLength: 1 /* Specify minimum characters required for showing */
    });
});