var backImage = new Array(); // don't change this

{% for bg_id in xrange(0, bg_count) %}
  backImage["{{ bg_id }}" + "_16"] = "url(/images/bgs/{{ bg_id }}_16.gif)";
  backImage["{{ bg_id }}" + "_32"] = "url(/images/bgs/{{ bg_id }}_32.gif)";
{% end %}

function changeBGImage(whichImage){
	$('#timeline').css("background-image", backImage[whichImage]);
}
