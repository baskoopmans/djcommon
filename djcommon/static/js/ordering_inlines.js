jQuery(function($) {
    $("div.inline-group").sortable({
        axis: 'y',
        placeholder: 'ui-state-highlight',
        forcePlaceholderSize: 'true',
        items: '.row1, .row2',
        update: update
    });
});

function update() {
    $('.row1, .row2').each(function(i) {
        $(this).find('input[id$=position]').val(i+1);
    });
}

jQuery(document).ready(function($){
    $(this).find('.original').hide().parent('tr').parent('tbody').parent('table').find("th[colspan='2']").removeAttr('colspan');
    $(this).find('input[id$=position]').parent('td').hide().parent('tr').parent('tbody').parent('table').find("th:contains('Position')").hide();
    $(this).find('input[id$=position]').parent('td').hide().parent('tr').parent('tbody').parent('table').css('cursor','move');
    $('.add-row a').click(update);
});