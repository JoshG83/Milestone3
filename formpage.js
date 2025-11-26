/* This starts our simple JavaScript code for handling the form interactions */
/* The first line looks for all input and textarea elements on a webpage */
$('.form').find('input, textarea').on('keyup blur focus', function (e) {
/* We start */
  var inputelement = $(this),
      label = inputelement.prev('label');



	  if (e.type === 'keyup') {
			if (inputelement.val() === '') {
          label.removeClass('active highlight');
        } else {
          label.addClass('active highlight');
        }
    } else if (e.type === 'blur') {
    	if( inputelement.val() === '' ) {
    		label.removeClass('active highlight'); 
			} else {
		    label.removeClass('highlight');   
			}   
    } else if (e.type === 'focus') {
      
      if( inputelement.val() === '' ) {
    		label.removeClass('highlight'); 
			} 
      else if( inputelement.val() !== '' ) {
		    label.addClass('highlight');
			}
    }

});

$('.tab a').on('click', function (e) {
  
  e.preventDefault();
  
  $(this).parent().addClass('active');
  $(this).parent().siblings().removeClass('active');
  
  target = $(this).attr('href');

  $('.tab-content > div').not(target).hide();
  
  $(target).fadeIn(600);

  
});