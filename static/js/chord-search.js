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
});