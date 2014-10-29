function basic_html_to_markdown(html) {
    return html.replace(/<p>/g, "")
        .replace(/<\/p>/g, "\n\n")
        .replace(/<br ?\/?>/g, "\n")
        .replace(/<\/?strong>/g, "**")
        .replace(/<\/?b>/g, "**")
        .replace(/<\/?em>/g, "*")
        .replace(/<\/?i>/g, "*");
}

$(document).ready(function(){
    $('#base-modal').modal({
        show: false
    });

    if ($('.warn').length) {
        $('.warn').on('click', function(e){
            e.preventDefault();

            var elem = $(this);

            $('#base-modal .message').text(elem.data('warning'));

            $('#base-modal .ok').on('click', function(){
                window.location = elem.attr('href');
                return true;
            });

            $('#base-modal').modal('show');
        });
    }

    if ($('.edit-tax').length) {
        $('.edit-tax').on('click', function(e){
            $('.tax-actions').slideToggle();
            $('.delete-checkbox').toggle();
        });
    }

    if ($('.rating').length) {
        $.getScript('/static/js/raty/jquery.raty.min.js', function(){
            $('.rating').raty({
                path: '/static/img',
                number: 4,
                size: 28,
                hints: ['Poor', 'Average', 'Good', 'Excellent'],
                score: function() {
                    return $(this).attr('data-score');
                },
                click: function(score) {
                    var params = {
                        book_id: $(this).data('book-id'),
                        score: score
                    };

                    $.post('/ajax/rate', params);
                }
            });
        });
    }

    if ($('.hierarchical-tax-list').length) {
        $.getScript('/static/js/bonsai/jquery.bonsai.js', function(){
            $('.hierarchical-tax-list').bonsai();
        });
    }

    if ($('.tax-list').length) {
        $('.tax-list a').on('click', function(e){
            var elem = $(e.target);

            $('#tax-id').val(elem.data('tax-id'));
            $('#tax-name').val(elem.data('tax-name'));
            $('#tax-parent').val(elem.data('tax-parent'));

            $('#taxonomy-edit-modal').modal();
        });
    }

    if ($('.reading-list-reposition').length) {
        $.getScript('/static/js/jquery-ui-1.10.4.custom.min.js', function(){
            $('#book-list').sortable({
                handle: '.reading-list-reposition',
                tolerance: 'pointer',
                stop: function(evt, ui) {
                    var data = {}
                    $('#book-list').find('.row').each(function(i, el) {
                        var book_id = $(this).data('book-id');
                        data[book_id] = i;
                    });

                    $.post('/ajax/order_reading_list', {'data': JSON.stringify(data)});
                }
            });
        });
    }

    if ($('#lookupTitle').length) {
        $('#lookupTitle').click(function(){
            var title = $('#title').val();

            $.getJSON('https://www.googleapis.com/books/v1/volumes?q=' + encodeURIComponent(title), function(data){
                if (data['totalItems'] > 0) {
                    // todo: allow choice. for now pick first
                    var item = data['items'][0]['volumeInfo'];
                    $('#author').val(item['authors'][0]);
                    $('#description').val(item['description']);
                }
            });
        });
    }

    if ($('#book-file').length) {
        $('#use-meta').on('click', function(){
            if ($('#use-title').is(':checked')) {
                $('#title').val($('#meta-title').text());
            }

            if ($('#use-author').is(':checked')) {
                $('#author').val($('#meta-author').text());
            }

            if ($('#use-publisher').is(':checked')) {
                $('#publisher').val($('#meta-publisher').text());
            }

            if ($('#use-description').is(':checked')) {
                $('#description').val(basic_html_to_markdown($('#meta-description').html().trim()));
            }

            if ($('#use-cover').is(':checked')) {
                $('#input-meta-cover').val($('.book-form').data('meta-cover'));
                $('#cover-from-meta').show();
                $('#cover').hide();
            }

            $('#meta-modal').modal('hide');
        });

        function replace_meta_cover_image(src) {
            var cover_div = $('#meta-cover');
            var cover = $('<img>');
            cover.attr('src', src);
            cover_div.html('');
            cover_div.append(cover);
            $('#use-cover').prop('checked', false);
        }

        $('#meta-modal').on('hidden', function(){
            replace_meta_cover_image('/static/img/default.jpg');
        });

        $.getScript('/static/js/uploadify/jquery.uploadify.min.js', function(){
            $('#book-file').uploadify({
                swf: '/static/js/uploadify/uploadify.swf',
                uploader: '/books/upload',
                buttonText: 'Select Book File',
                multi: false,
                removeCompleted: false,
                onUploadSuccess: function(file, data, response) {
                    var json = $.parseJSON(data);

                    $('#file').val(json.filename);
                    var meta = json.meta;

                    if (meta) {
                        $('#meta-title').text(meta.title);
                        $('#meta-author').text(meta.author);
                        $('#meta-publisher').text(meta.publisher);
                        $('#meta-description').html(meta.description);

                        if (meta.cover) {
                            replace_meta_cover_image('/static/uploads/tmpcovers/' + meta.cover);
                            $('.book-form').data('meta-cover', meta.cover);
                            $('#use-cover').prop('checked', true);
                        }

                        $('#meta-modal').modal();
                    }
                }
            });
        });
    }

    if ($('.add-to-reading-list').length) {
        $('.add-to-reading-list').on('click', function(e) {
            var elem = $(this);
            var book_id = elem.data('book-id');
            $.post('/ajax/add_to_reading_list', {'book_id': book_id}, function(){
                elem.addClass('btn-success');
                elem.find('i').removeClass('icon-list').addClass('icon-ok').addClass('icon-white');
            });
        });
    }

    if ($('.remove-from-reading-list').length) {
        $('.remove-from-reading-list').on('click', function(e) {
            var book_id = $(this).data('book-id');
            $(this).closest('.row').fadeOut();
            $.post('/ajax/remove_from_reading_list', {'book_id': book_id});
        });
    }
});