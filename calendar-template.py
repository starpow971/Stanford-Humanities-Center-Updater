# Copyright 2011, The Board of Regents of Leland Stanford, Jr. University
# All rights reserved. See LICENSE. 
# Author: Christine Williams <christine.bennett.williams@gmail.com>
# Description: Templates events into nice-looking calendar html.


from Cheetah.Template import Template

#TODO: figure out how to get template as a file to work.
templateDef = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>

	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<link rel="icon" href="http://shc.stanford.edu/favicon.ico" type="image/x-icon" />
		<link rel="shortcut icon" href="http://shc.stanford.edu/favicon.ico" type="image/x-icon" />
		
		<title>Calendar | Stanford Humanities Center</title>
		
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/styles.css"  />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/colourtag.css"  />
		
		<!--[if lt IE 7]>
		<script type="text/javascript">
			if (navigator.platform == "Win32" && navigator.appName == "Microsoft Internet Explorer" && window.attachEvent) {
				window.attachEvent("onload", enableAlphaImages);
			}

			function enableAlphaImages(){
				var rslt = navigator.appVersion.match(/MSIE (\d+\.\d+)/, '');
				var itsAllGood = (rslt != null && Number(rslt[1]) >= 5.5);
				if (itsAllGood) {
					for (var i=0; i<document.all.length; i++){
						var obj = document.all[i];
						var bg = obj.currentStyle.backgroundImage;
						var img = document.images[i];
						if (bg && bg.match(/\.png/i) != null) {
							var img = bg.substring(5,bg.length-2);
							var offset = obj.style["background-position"];
							obj.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+img+"', sizingMethod='crop')";
							obj.style.backgroundImage = "url('../../rw_common/themes/blueballfreestack/blank.gif')";
							obj.style["background-position"] = offset; // reapply
						} else if (img && img.src.match(/\.png$/i) != null) {
							var src = img.src;
							img.style.width = img.width + "px";
							img.style.height = img.height + "px";
							img.style.filter = "progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+src+"', sizingMethod='crop')";
							img.src = "../../rw_common/themes/blueballfreestack/blank.gif";
						}

					}
				}
			}
		</script>
		
		<style>
		.clearfix{ display: inline-block; }
		</style>
		<![endif]-->
		
		<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.2/jquery.min.js" type="text/javascript"></script>
		
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/pagewidth/width960.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/fontscontent/helvetica_content.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/fontsheadline/helvetica_headline.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/titlealign/title_center.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/sloganalign/slogan_right.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/sidebarheadalign/sidebarheader_left.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/footeralign/footer_center.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/breadcrumbalign/breadcrumb_left.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/pageshadow/shadow70.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/pagemargintop/pagemargintop_20.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/pagemarginbottom/pagemarginbottom_20.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/bodybg/bodybgimghide.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/bodybgposition/bodybgposition_topleft.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/bodybgrepeat/bodybgrepeat.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/pagewrappertrans/pagewrapper_no_transparent.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/wrapperbg/wrapperbgimghide.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/wrapperbgposition/wrapperbgposition_topleft.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/wrapperbgrepeat/wrapperbgrepeat.css" />
		<link rel="stylesheet" type="text/css" media="screen" href="../../rw_common/themes/blueballfreestack/css/customimage/customimg02.css" />
		
		<style type="text/css" media="all">h1{
color: #99000;
}

h4{
color: #99000;
}</style>
		
		<script type="text/javascript" src="../../rw_common/themes/blueballfreestack/javascript.js"></script>
		
		<script type="text/javascript">
			 <script src="assets/behaviour.js" type="text/javascript"></script>
<script src="assets/search.js" type="text/javascript"></script> 
		</script>

		
		<link rel='stylesheet' type='text/css' media='all' href='../../rw_common/plugins/stacks/stacks.css' />
		<!--[if IE]>
			<link rel='stylesheet' type='text/css' media='all' href='../../rw_common/plugins/stacks/stacks_ie.css' />
		<![endif]-->
		<link rel='stylesheet' type='text/css' media='all' href='index_files/stacks_page_page107.css' />
		<script type='text/javascript' charset='utf-8' src='index_files/stacks_page_page107.js'></script>

		
		
	<!-- Start Google Analytics -->
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-10321397-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script><!-- End Google Analytics -->
</head>
	
	<!-- This page was created using the Blueball FreeStack theme from Blueball Design. http://www.blueballdesign.com -->
	
	<body>
	
	<div id="pagecontainer">

		<div id="pagewrapper">
			

<!-- Stacks v1.4.4 -->
<div class='stacks_top'>
<div id='stacks_out_26149_page107' class='stacks_out'><div id='stacks_in_26149_page107' class='stacks_in'>
<div id='stacks_out_26151_page107' class='stacks_out'><div id='stacks_in_26151_page107' class='stacks_in'>
<div class='stacks_div stacks_left'>
<div id='stacks_out_26153_page107' class='stacks_out'><div id='stacks_in_26153_page107' class='stacks_in'>

<div id="logo"><a href="http://shc.stanford.edu/" ><img src="../../rw_common/images/weblogo.jpg" width="231" height="95" alt="Site logo"/></a></div>

<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_clear_right'></div>
<div class='stacks_div stacks_right'>
<div id='stacks_out_26155_page107' class='stacks_out'><div id='stacks_in_26155_page107' class='stacks_in'>
<div id='stacks_out_26157_page107' class='stacks_out'><div id='stacks_in_26157_page107' class='stacks_in'>
<div id="cse-search-form" style="width: 15em; float:right">Loading</div>
<script src="//www.google.com/jsapi" type="text/javascript"></script>
<script type="text/javascript"> 
  google.load('search', '1', {language : 'en'});
  google.setOnLoadCallback(function() {
    var customSearchControl = new google.search.CustomSearchControl('006956015087856419725:x6kfmzftfri');
    customSearchControl.setResultSetSize(google.search.Search.FILTERED_CSE_RESULTSET);
    var options = new google.search.DrawOptions();
    options.enableSearchboxOnly("http://shc.stanford.edu/search/index.html");
    customSearchControl.draw('cse-search-form', options);
  }, true);
</script>
<link rel="stylesheet" href="//www.google.com/cse/style/look/default.css" type="text/css" />
<div style="text-align: right"> <a href="/about/">About</a> | <a href="/room-reservations/">Room Reservations</a> | <a href="/contact-us/">Contact Us</a> | <a href="/people/">People</a> | <a href="/support/">Support</a>&nbsp;|&nbsp;
</div>

<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26159_page107' class='stacks_out'><div id='stacks_in_26159_page107' class='stacks_in'>
<div id="slogan"></div>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26160_page107' class='stacks_out'><div id='stacks_in_26160_page107' class='stacks_in'>
<div id="stacks_in_26160_page107_nav1"><div id="nav"><ul><li><a href="../../" rel="self">Home</a></li><li><a href="../../whats-new/" rel="self">What's New</a></li><li><a href="../../events/" rel="self" class="currentAncestor">Events</a><ul><li><a href="../../events/calendar/" rel="self">Calendar</a></li></ul></li><li><a href="../../fellowships/" rel="self">Fellowships</a><ul><li><a href="../../fellowships/non-stanford-faculty/" rel="self">External Faculty</a></li><li><a href="../../fellowships/arts/" rel="self">Arts Writer/Practitioner</a></li><li><a href="../../fellowships/stanford-faculty/" rel="self">Stanford Faculty</a></li><li><a href="../../fellowships/stanford-graduate-students/" rel="self">Stanford Graduate Students</a></li><li><a href="../../fellowships/stanford-undergraduates/" rel="self">Stanford Undergraduates</a></li><li><a href="../../fellowships/resources/" rel="self">Resources for Fellows</a><ul><li><a href="../../fellowships/resources/faq/" rel="self">Fellowship FAQ</a></li><li><a href="../../fellowships/resources/center-policies/" rel="self">Humanities Center Policies</a></li><li><a href="../../fellowships/resources/office-help/" rel="self">Office Help and Facilities</a></li><li><a href="../../fellowships/resources/university-policies/" rel="self">University and Building Policies</a></li><li><a href="../../fellowships/resources/stanford-resources/" rel="self">Stanford Resources</a></li><li><a href="../../fellowships/resources/emergency-policies/" rel="self">Emergency Policies</a></li></ul></li></ul></li><li><a href="../../workshops/" rel="self">Workshops</a><ul><li><a href="../../workshops/current-workshops/" rel="self">Current Workshops</a></li><li><a href="../../workshops/calendar/" rel="self">Workshop Calendar</a></li><li><a href="../../workshops/coordinators-directory/" rel="self">Coordinators Directory</a></li><li><a href="../../workshops/undergraduate-humanities-circle/" rel="self">Undergraduate Humanities Circle</a></li><li><a href="../../workshops/dissertation-writing-group/" rel="self">Dissertation Writing Group</a></li><li><a href="../../workshops/resources/" rel="self">Workshop Resources</a><ul><li><a href="../../workshops/resources/coordinator-guidelines/" rel="self">Coordinator Guidelines</a></li><li><a href="../../workshops/resources/coordinator-responsibilities/" rel="self">Coordinator Responsibilities</a></li><li><a href="../../workshops/resources/policies/" rel="self">Policies</a></li><li><a href="../../workshops/resources/financial/" rel="self">Financial Policies</a></li><li><a href="../../workshops/resources/expenses/" rel="self">Expenses</a></li><li><a href="../../workshops/resources/visas/" rel="self">Visas</a></li><li><a href="../../workshops/resources/forms/" rel="self">Forms and Links</a></li></ul></li></ul></li><li><a href="../../international-programs/" rel="self">International & Arts Programs</a><ul><li><a href="../../international-programs/international-visitors/" rel="self">International Visitors</a></li><li><a href="../../international-programs/arts-fellowship/" rel="self">Arts Writer/Practitioner Fellowship</a></li></ul></li><li><a href="../../videos-digital/" rel="self">Videos & Digital</a><ul><li><a href="../../videos-digital/videos/" rel="self">Videos</a></li><li><a href="../../videos-digital/digital-humanities/" rel="self">Digital Humanities</a></li></ul></li><li><a href="../../students/" rel="self">Stanford Students</a></li></ul></div></div>


<script type="text/javascript">
jQuery(document).ready(function ($) {
$('#stacks_in_26160_page107').parent().css({ 'overflow': 'visible', 'z-index': '9999' });       
}); 
</script>



<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26161_page107' class='stacks_out'><div id='stacks_in_26161_page107' class='stacks_in'>
<div id='stacks_out_26163_page107' class='stacks_out'><div id='stacks_in_26163_page107' class='stacks_in'>
<div id="breadcrumbcontainer"><ul><li><a href="../../">Home</a>&nbsp;/&nbsp;</li><li><a href="../../events/">Events</a>&nbsp;/&nbsp;</li><li><a href="./">Calendar</a>&nbsp;/&nbsp;</li></ul></div>

<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26164_page107' class='stacks_out'><div id='stacks_in_26164_page107' class='stacks_in'>
<div class='stacks_div stacks_left'>
<div id='stacks_out_26166_page107' class='stacks_out'><div id='stacks_in_26166_page107' class='stacks_in'>

<div id="sidebar">
<div class="sideHeader"></div>
<a href="/events/calendar/">Calendar</a><br/><br/>
<a href="/workshops/calendar/">2011-12 Workshop Calendar</a><br><br>
<a href="/events/calendar/arts-international/">2011-12 Arts and International Calendar</a><br />

</div>





<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26167_page107' class='stacks_out'><div id='stacks_in_26167_page107' class='stacks_in'>
<span style="font-size:13px; "><hr></span><span style="font-size:13px; font-weight:bold; "><br /></span><span style="font-size:13px; font-weight:bold; "><a href="../../events/" rel="self" title="Events">Add me to the events notification list!</a></span><span style="font-size:13px; font-weight:bold; "><br /></span>
<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26169_page107' class='stacks_out'><div id='stacks_in_26169_page107' class='stacks_in'>
<span style="color:#000000;"><hr></span><span style="color:#70694E;"><br /></span><span style="color:#70694E;"><a href="../../events/presidential-lectures/" rel="self" title="Presidential Lectures">Presidential Lectures<br /></a></span><span style="color:#70694E;"><br /></span><span style="color:#70694E;"><a href="../../events/marta-sutton-weeks/" rel="self" title="Marta Sutton Weeks Distinguished Visitors">Marta Sutton Weeks Distinguished Visitors</a></span><span style="color:#70694E;"><br /><br /></span><span style="color:#70694E;"><a href="../../events/harry-camp/" rel="self" title="Harry Camp Memorial Lectures">Harry Camp Memorial Lectures</a></span><span style="color:#70694E;"><br /><br /></span><span style="color:#70694E;"><a href="../../events/raymond-west/" rel="self" title="Raymond F. West Memorial Lectures">Raymond F. West Memorial Lectures</a></span><span style="color:#70694E;"><br /><br /></span><span style="color:#70694E;"><a href="../../events/bliss-carnochan/" rel="self" title="Bliss Carnochan Lectures">Bliss Carnochan Lectures</a></span><span style="color:#70694E;"><br /></span>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_div stacks_right'>
<div id='stacks_out_26174_page107' class='stacks_out'><div id='stacks_in_26174_page107' class='stacks_in'>
All events take place at Stanford University, unless otherwise noted.<br /><br /><br />The Calendar of Events lists events sponsored and co-sponsored by the Stanford Humanities Center.  For a more comprehensive listing of university-wide events, see the <a href="http://events.stanford.edu/" rel="external">Stanford Event Calendar.</a>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_div stacks_middle'>
<div id='stacks_out_26177_page107' class='stacks_out'><div id='stacks_in_26177_page107' class='stacks_in'>
<h1>Events Calendar</h1><br /><br /><h2>Upcoming Events</h2><br /><br /><span style="font-size:11px; ">$calendar_title</span><span style="font-size:13px; "><br /></span><span style="font-size:14px; color:#70694E;font-weight:bold; ">$event_title</span><span style="font-size:13px; "><br />$date | $start_time-$end_time | $location<br /><br /><hr><br /></span><div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26179_page107' class='stacks_out'><div id='stacks_in_26179_page107' class='stacks_in'>
<div class='stacks_div stacks_left'>
<div id='stacks_out_26181_page107' class='stacks_out'><div id='stacks_in_26181_page107' class='stacks_in'>
<span style="color:#70694E;"><< Older Events</span>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_clear_right'></div>
<div class='stacks_div stacks_right'>
<div id='stacks_out_26184_page107' class='stacks_out'><div id='stacks_in_26184_page107' class='stacks_in'>
<p style="text-align:right;"><span style="color:#70694E;">Newer Events >></span></p>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
</div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>
<div id='stacks_out_26186_page107' class='stacks_out'><div id='stacks_in_26186_page107' class='stacks_in'>
<div id='stacks_out_26188_page107' class='stacks_out'><div id='stacks_in_26188_page107' class='stacks_in'>

<div id="footer">&copy; 2011 <a href="http://www.stanford.edu">Stanford University</a> | <a href="/site-map/">Site Map</a> | <a href="http://www.stanford.edu/site/terms.html">Terms of Use</a> | <a href="http://www.stanford.edu/site/copyright.html">Copyright Complaints</a> | 424 Santa Teresa St. Stanford, CA 94305</div>

<div class='stacks_clearer'></div></div></div>
<div class='stacks_clearer'></div>
<div class='stacks_clearer'></div></div></div>

<div class='stacks_clearer'></div>
</div>
<!-- End of Stacks Content -->



		</div>
		
	</div>

	</body>

</html>"""

class CalendarTemplate(Template):
#TODO: figure out importing variables from database?
	calendar_title = 'STANFORD HUMANITIES CENTER EVENTS'
	event_title = 'Salon Featuring MK Raina'
	date = 'Tuesday, October 11, 2011'
	start_time = '4'
	end_time = '6 pm'
	location = 'Humanities Center Board Room'
	
t2 = CalendarTemplate(templateDef)

print t2