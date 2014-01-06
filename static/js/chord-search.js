$(document).ready(function () {
    if (!$("#q").is(":focus")) {
        $("#q").focus();
    }
    $("#crd").select2({
        width: 'element',
        placeholder: 'Chords',
        quietMillis: 100,
        openOnEnter: false,
        allowClear: true,
        minimumInputLength: 1,
        multiple: true,
        width: 'resolve',
        initSelection: function (element, callback) {
            var initialValue = $(element).val();
            if(!initialValue)
                return;
            var valueObj = eval($(element).val());
            $(element).val($.map(valueObj, function(v){ return v.id; }).join(","));
            callback(valueObj);
        },
        ajax: {
            url: '/chord_filter',
            dataType: 'json',
            data: function (term, page) {
                return { q: term };
            },
            results: function (data, page) {
                return {
                    results: data.results
                };
            }
        },
        formatResult: function (chord) {
            return chord.name;
        },
        formatSelection: function (chord) {
            return chord.name;
        }
    });
    var validator = $('#search-form').validate({
            ignore: 'input[type=hidden]',
            errorPlacement: function (error, element) {
            },
            errorClass: 'has-error'
        });
});