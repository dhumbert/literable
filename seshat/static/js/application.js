(function(){
    $('#base-modal').modal();

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

    $('.rating').raty({
        path: 'static/img',
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
})();