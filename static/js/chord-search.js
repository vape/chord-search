$(document).ready(function () {
    if(!$("#q").is(":focus")){
        $("#q").focus();
    }
    $("#crd").select2({
        width: 'element',
        placeholder: 'Chords',
        openOnEnter: false,
        allowClear: true
    });
    var validator = $('#search-form').validate(
        {
            ignore: 'input[type=hidden]',
            errorPlacement: function(error, element) {},
            errorClass:'has-error'
        });
});