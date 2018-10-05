/* Project specific Javascript goes here. */
if (!$) {
    $ = django.jQuery;
}

download_file = function(pk) {
  $('input[name="_selected_action"]').removeAttr('checked');
  $('input[name="_selected_action"][value="{}"]'.replace('{}', pk)).attr('checked', 'checked');
  $('select[name="action"]').val('download');
  $('button[type="submit"][name="index"]').click();
};
