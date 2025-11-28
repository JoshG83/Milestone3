/* This starts our simple JavaScript code for handling the form interactions */
/* The first line looks for all input and textarea elements on a webpage */
$('.form').find('input, textarea').on('keyup blur focus', function (e) {
/* We start by creating a variable called inputelement that acts as the current input of the textarea. */
  var inputelement = $(this),
  /* We then create a variable called label that finds the previous label element before the input or textarea. */
      label = inputelement.prev('label');


  /* This section handles multiple events that can occur on the webpage: keyup, blur, and focus */
  /* The keyup event occurs when the user types something into the input or textarea, which can be anything so long as the field allows it */
  /* The if statement here is saying that if the input area is blank, remove the active highlight, otherwise add the active highlight. */
	  if (e.type === 'keyup') {
			if (inputelement.val() === '') {
          label.removeClass('active highlight');
        } else {
          label.addClass('active highlight');
        }
  /* The blur event occurs when the user clicks away from the input or textarea */
  /* The if statement here is saying that if the input area is blank, like above, remove the active highlight. */
  /* Otherwise, the highlight will just be removed */
    } else if (e.type === 'blur') {
    	if( inputelement.val() === '' ) {
    		label.removeClass('active highlight'); 
			} else {
		    label.removeClass('highlight');   
			}   
  /* Lastly, the focus event will occur when the user clicks into the input or textarea */
  /* Basically, if the input area is blank, the highlight will be removed, if there is anything but blank in the input it will be highlighted. */
    } else if (e.type === 'focus') {
      
      if( inputelement.val() === '' ) {
    		label.removeClass('highlight'); 
			} 
      else if( inputelement.val() !== '' ) {
		    label.addClass('highlight');
			}
    }

});


/* This section handles the tabbed content on the webpage */
/* When a user clicks on a tab, the corresponding content will be displayed while hiding the other content */
$('.tab a').on('click', function (e) {
/* Prevent the default action of the click event, we want to circumvent the page jumping to content immediately. */
  e.preventDefault();
/* Add the active class to the clicked tab or link and remove it from its siblings. Basically, the active class is activated when one link is clicked, others are ignored. */
  $(this).parent().addClass('active');
  $(this).parent().siblings().removeClass('active');
/* We then create a variable called target that gets the href attribute of the selected link. This will be used to identify which content to show. */
  target = $(this).attr('href');
/* We then want hide all tab content that does not match the target variable. */
  $('.tab-content > div').not(target).hide();
  /* Finally, we want to fade in the target content over 600 milliseconds for a smooth transition */
  $(target).fadeIn(600);

  
});