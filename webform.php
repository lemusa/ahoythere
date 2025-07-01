<?php
$to = "admin@ahoythere.co.nz" ;
$from = $_REQUEST['Email'] ;
$name = $_REQUEST['Name'] ;
$headers = "From: $from";
$subject = "Enquiry";

$fields = array();
$fields{"Name"} = "Name";
$fields{"Email"} = "Email";
$fields{"Message"} = "Message";

$body = "Message from ahoythere:\n"; foreach($fields as $a => $b){ $body .= sprintf("%20s: %s\n",$b,$_REQUEST[$a]); }

$headers2 = "From: noreply@ahoythere.co.nz";
$subject2 = "Thank you for contacting ahoythere!";
$autoreply = "Thank you for contacting ahoythere. If you're expecting a reply you will probaly get one soon, if not then no one cares";

if($from == '') {print "You have not entered an email, please go back and try again";}
else {
if($name == '') {print "You have not entered a name, please go back and try again";}
else {
$send = mail($to, $subject, $body, $headers);
$send2 = mail($from, $subject2, $autoreply, $headers2);
if($send)
{header( "Location: sent.html" );}
else
{print "We encountered an error sending your mail, please notify admin@ahoythere.co.nz"; }
}
}
?>
