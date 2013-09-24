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
                hints: ['Poor', 'Average', 'Good', 'Excellent'],
                score: function() {
                    return $(this).attr('data-score');
                },
                click: function(score) {
                    var params = {
                        book_id: $(this).data('book-id'),
                        score: score
                    };

                    $.post('/ajax/rate', params, function(data){
                        console.log(data);
                    });
                }
            });
        });
    }
});