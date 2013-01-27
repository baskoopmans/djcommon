/* collapsed_tabular_inlines.js */
/* Created in August 2012 by Bas Koopmans */
/* Use, distribute and modify freely */

jQuery(function($) {
    // Only for stacked inlines
    $('div.inline-group div.inline-related:not(.stacked)').each(function() {
        fs = $(this).find('fieldset').addClass('collapse')
        h2 = $(this).find('h2:first')

        // Don't collapse if fieldset contains errors
        if (fs.find('[class^=error]').length != 0){
            fs.removeClass('collapsed');
            fs.find('tr').not('.has_original').find('.delete').html('<div><a class="inline-deletelink" href="javascript:void(0)">Verwijderen</a></div>');
        }
        else {
            fs.addClass('collapsed');
        }

        // Add toggle link
        h2.append(' <a class="collapse-toggle" href="#">(' + gettext('Show') + ')</a> ');
        h2.find('a.collapse-toggle').on("click", function(){
            fs = $(this).parent('h2').parent('fieldset');
            if (!fs.hasClass('collapsed'))
            {
                fs.addClass('collapsed');
                $(this).html('(' + gettext('Show') + ')');
            }
            else
            {
                fs.removeClass('collapsed');
                $(this).html('(' + gettext('Hide') + ')');
            }
        }).removeAttr('href').css('cursor', 'pointer');
    });
});