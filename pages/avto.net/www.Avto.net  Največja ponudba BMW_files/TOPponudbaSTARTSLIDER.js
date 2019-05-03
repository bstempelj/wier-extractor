	jQuery(document).ready(function(){
		jQuery('#slider-stage').carousel('#previous', '#next');
		jQuery('#viewport').carousel('#simplePrevious', '#simpleNext');  
	});
	//The auto-scrolling function
	function slide(){
	  $('#simpleNext').click();
	}
	//Launch the scroll every 5 seconds
	var intervalId = window.setInterval(slide, 5000);
	
	//On user click deactivate auto-scrolling
	$('#previous, #simpleNext').click(
	 function(){
	  window.clearInterval(intervalId);
	 }
	);