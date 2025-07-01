#!/usr/bin/perl
# Change the line above to match the path to perl on your server
#
# YOU MUST ALSO REVIEW THE VALUES IN THE FILE uniformmail.params

# use strict;
# strict should be used for development only. It should be commented out when deployed.

use Net::SMTP;
use URI::Escape;
use HTTP::Date;

#################### UNIFORMMAIL V 1.0.01 ########################
#
# YOU MUST NOT NOT REMOVE OR EDIT ANY PART OF THIS NOTICE
#
# declare program name/version
use constant SCRIPT_NAME     => 'uniformmail';
use constant PROGRAM_NAME    => 'Uniform Mail';
use constant PROGRAM_VERSION => '1.0.01';
use constant PROGRAM_URL     => 'http://www.skaro.net';
#
# Copyright James D H Turner 2004-2007
# Published by Cathonian Software and SKARO.NET
#
# UniFormMail is designed to send HTML form data to a specified
# email address or addresses.
#
# This program may be used in isolation but it is designed to work
# with the javascript file uniformmail.js to perform validation.
#
# This program may be used in private or commercial websites
# without charge.
#
# If you use this program, must place a link to
#   http://www.skaro.net
# on your website with a message that reads something like
#   Form Mail by SKARO.NET
#
# This program is supplied without any warranty of any sort.
# If you use this program, you must accept all liablity for
# losses that may result. You should test this program
# thoroughly before deployment.
#
# You may modify this program but you may not redistribute any
# such modified versions.
#
# For the complete license terms, visit
#   http://www.skaro.net/uniformmail
#
# Please report bugs, etc. via the website.
#
################################################################
#
# This script expects to receive form data by the POST method.
# However, it also requires :- 
#   a file containing parameter data called uniformmail.params
#   command-line parameters
#
# Parameters take the form name1=value1&name2=value2.
# Refer to the PARAM_ values below for a list of parameter names.
#
################################################################

# declare miscllaneous contants
use constant DEFAULT_TIMEOUT => 20;
use constant ECUSTOM_PREFIX   => 'MAIL ERROR: ';

# declare the recognised parameter names
use constant PARAM_PARAMS   => 'params';     # name of params file
use constant PARAM_SERVER   => 'mailserver'; # smtp server
use constant PARAM_TIMEOUT  => 'timeout';    # Wait period for connection. Default defined above.
use constant PARAM_TO       => 'to';         # Primary email address
use constant PARAM_CC       => 'cc';         # Comma or semicolon limited list of copy addresses
use constant PARAM_BCC      => 'bcc';        # As cc except that values are not printed in the header
use constant PARAM_RETURN   => 'return';     # Return-Path: null is normally ok.
use constant PARAM_FROM     => 'from';
use constant PARAM_REPLYTO  => 'replyto';
use constant PARAM_SUBJECT  => 'subject';
use constant PARAM_PRIORITY => 'priority';
use constant PARAM_VERIFY   => 'verify';  # request recipient addresses are verified
use constant PARAM_TICKET   => 'ticket';  # filename of counter. Optional initial value separated by comma.
use constant PARAM_SUCCESS  => 'success'; # url of success page.
use constant PARAM_ERROR    => 'error';   # url of error   page.
use constant PARAM_DEBUG    => 'debug';   # output smtp headers.
use constant PARAM_BODY     => 'body';    # email body - short texts only %0D = linebreak
                                          # if defined, POST data is ignored

# Declare global vars - required for strict compilation
use vars qw(
  $exception
  $logfile
  $url_success
  $url_error

  $paramfile %fileparams %urlparams
  $domain
  $referrer
  $mailserver
  $verify
  $ticket $ticketfile $ticketbase $ticketvalue
  $timeout
  $subject
  $priority
  $debug

  $body @inputdata @reply

  $return $to $cc $bcc $from $replyto

  $accept_addrs $accept_count
  $reject_addrs $reject_count

  $reply_begun

  $smtp
);

sub raise_ECustom # ($message)
{ $exception = shift; unless ($exception) { return }

  $exception = ECUSTOM_PREFIX."$exception\n";
# adding a linefeed prevents line number info being added by die method.

  die($exception);
}

sub is_Ecustom # ($message)
{ my $msg = shift; unless($msg) { return 0 }
  my $ep  = '^'.ECUSTOM_PREFIX;

  return ($msg =~ /$ep/)
}

sub add_line # ($lines,$newline)
# result always ends with \n
{ my ($lines,$newline) = @_; unless ($lines) { $lines = '' };

  if ($newline) { $lines = "$lines$newline\n" }

  return $lines;
}

sub print_css
{ unless (open(CSS, '<'.SCRIPT_NAME.'.css')) { return };
  my @lines = <CSS>; chomp(@lines);
  close(CSS);

  print "  <STYLE>\n  <!--\n";
  my $line; foreach $line (@lines) { print "    $line\n" }
  print "  -->\n  </STYLE>\n";  
}

sub begin_reply
{ if ($reply_begun) { return }; $reply_begun = 1;

# Begin the http header
# There are several ways to switch off caching depending on which version of HTTP is in use.
# You may try other methods if the method chosen below fails.
# print "Expires: -1\n";
# print "Pragma: no-cache\n";

  print "Content-type: text/html\n";
  print "Cache-Control: no-cache\n";

  my $tmp;
  if ($exception) { $tmp = $url_error   }
             else { $tmp = $url_success }

  if ($tmp and !$debug) { print "Location: $tmp\n" }

# Terminate HTTP header block with a blank line
  print "\n";

# Print the html head
  $tmp = PROGRAM_NAME;
  if ($exception) { $tmp = $tmp.' : ERROR' } else
              { $tmp = $tmp.' : Confirmation' } 
  print "<HTML>\n<HEAD>\n";
  print "  <TITLE>$tmp</TITLE>\n";
  print '  <META NAME="robots" CONTENT="noindex">';
  print "\n";

  print_css;
  print "</HEAD>\n<BODY>\n";
}

sub end_reply
{ print "</BODY>\n</HTML>\n"
}

sub handle_exception
{ my $msg = shift; unless ($msg) { return }

# record error message in error log.
  print STDEXCPT SCRIPT_NAME.": $msg\n";

  begin_reply;

  $msg = tohtml($msg);
  print "$msg<BR>\n";
}

sub extract_domain # ($url)
{ my $result = shift;
  if ($result) {
    $result =~ s/.*\/\///;  # strip everything up to and including //
    $result =~ s/^www\.//i; # strip www. if present (case insensitive)
    $result =~ s/\/.*//;    # strip path if present
    $result =~ s/:.*//;     # strip port number if present
  }

  return $result;
}

sub trim_paramline # ($line)
{ my $line = shift; unless ($line) { return }

  $line =~ s/#.*//;      # trim everything after '#' char

  if ($line !~ /=/) { return }; # reject any line that does not include '=' char

  $line =~ s/\s*=\s*/=/; # trim white space on either side of '=' char
  $line =~ s/^\s*//;     # trim white space at start of line
  $line =~ s/\s*$//;     # trim white space at end   of line

  return $line;
}

sub validate_int # ($str)
# Validates unsigned integer. Returns 0 if invalid.
# Hex requires h as a suffix. Returns hex integer or zero.
# $str must be less than 10 chars long.
{ my $str = shift; if (!$str or (length($str) > 9)) { return 0 }
  my $hex = ($str =~ s/[hH]$//);
  my $x;

  if ($hex) { $x = '[^0-9a-fA-F]' } else { $x = '\D' }

  if ($str =~ /$x/) { return 0        }
  if ($hex)         { return $str.'h' }

  return $str;
}

sub get_ticket # ($ticketfile,$ticketbase)
{ my $tf = shift; unless ($tf) { return  }
  my $tb = shift; unless ($tb) { $tb = 0 }

  my $hex = ($tb =~ s/[hH]$//); if ($hex) { $tb = hex($tb) }

  my $result = $tb;

  if (-e $tf) {
    if (open(TICKET_FILE, "<$tf")) {
      $result = <TICKET_FILE>;
      close(TICKET_FILE);
    }
    else { return 'TICKET ERROR - READ' }
  }

  $result = validate_int($result) + 1;

  if (open(TICKET_FILE, ">$tf")) {
    print(TICKET_FILE "$result");
    close(TICKET_FILE);
  }
  else { return 'TICKET ERROR - WRITE' }

# convert to hex
  if ($hex) { $result = sprintf('%04X',$result) }

  return $result;
}

sub read_fileparams
# Read parameter data from the file specified by $paramfile.
# If the $paramfile is null or the file does not exist, a default is used.
# A global var is used rather than a parameter so that the actual file used is reported when debugging.
{ unless ($paramfile and (-e $paramfile)) { $paramfile = SCRIPT_NAME.'.params' }

  unless (-e $paramfile)          { raise_ECustom("File not found - $paramfile") }
  unless (open(HF,"<$paramfile")) { raise_ECustom("Unable to open file - $paramfile") }

  my (@lines, $line, $k, $v);
  
  @lines = <HF>; close(HF); chomp(@lines);

  foreach (@lines) {
    $line = trim_paramline($_);
    if ($line) {
      ($k, $v) = split('=',$line,2); # split line into two on the first '='
      if ($k and defined($v)) { $fileparams{"$k"} = $v }
  }}

# read parameters for which there is no command-line equivalent
  $domain   = $fileparams{'domain'};
  $referrer = $fileparams{'referrer'};
  $referrer = extract_domain($referrer); # clean up - remove www. prefix if present

  $ticket   = PARAM_TICKET;
  $ticket   = $fileparams{$ticket};
  if (($ticket) and ($ticket ne '!')) { 
    ($ticketfile,$ticketbase) = split(/\s*,\s*/,$ticket,2);
    if ($ticketbase) { $ticketbase = validate_int($ticketbase) }
                else { $ticketbase = 0 }

    $ticketvalue = get_ticket($ticketfile,$ticketbase);
  }

# detect the domain if none is specified
  if ((!$domain) or ($domain eq '*') or ($domain eq '!')) { $domain = $ENV{'SERVER_NAME'} };

# clean up domain - mostly worried about unwanted 'www.' prefix
  $domain = extract_domain($domain);

  if ($referrer) {
    if    ($referrer eq '*') { $referrer = $domain }
    elsif ($referrer eq '!') { $referrer = ''      }
  }
}

sub read_param # ($name)
{ my $name  = shift;
  my $param = $fileparams{$name};

  if ($param) { if ($param eq '!') { return '' } else { return $param } }

  $param = $urlparams{$name}; unless ($param) { $param = '' }
  
  return $param;
}

sub read_addr # ($name)
{ my $name   = shift;
  my $fparam = $fileparams{$name};
  my $uparam = $urlparams {$name}; if ($uparam) { $uparam =~ s/::/@/g }

# ensure vars are initialized
  unless ($fparam) { $fparam = '' }
  unless ($uparam) { $uparam = '' }

# if param is disabled return ''
  if ($fparam eq '!') { return '' }

# replace * with domain name
  $fparam =~ s/\*/$domain/g;

# if fparam contains '@' return it
  if ($fparam =~ /@/) { return $fparam }

# if fparam <> '', insert it into uparam as the domain
  if ($fparam) {
    $fparam = '@'.$fparam;
    $uparam =~ s/@\*?/$fparam/g;
  }

  return $uparam;
}

sub url_decode # ($s,$unplus)
# decodes an url-encoded string and normalises linebreaks.
# if $unplus is true, '+' chars are replaced with spaces.
{ my $s      = shift;
  my $unplus = shift;

  if ($s) {
    if ($unplus) { $s =~ s/\+/ /g };
    $s = uri_unescape($s);
    $s =~ s/\r\n/\n/g;    # normalise CRLF linebreaks (Windows)
    $s =~ s/\r/\n/g;      # normalise CR   linebreaks (Mac)
  }

  return $s;
}

sub read_urlparams
# reads key=value parameter pairs in the query part of the url.
# The value part of each argument is url-decoded and linebreaks are normalised.
{ my ($q,@q,$k,$v);

  $q = $ENV{'QUERY_STRING'};
  @q = split('&',$q);

  foreach (@q) {
    ($k,$v) = split('=',$_,2);
    if ($k) {
      if ($v) { $v = url_decode($v,0) } else { $v = '' }
      $urlparams{"$k"} = $v;
  }}
}

sub get_params {
  read_urlparams;

# check if a param file has been specified in the command line
  $paramfile = PARAM_PARAMS;
  $paramfile = $urlparams{$paramfile};  

# load the param file. If the specified file does not exist the default is loaded.
  read_fileparams;

# read address parameters
  $to      = read_addr(PARAM_TO);
  $cc      = read_addr(PARAM_CC);
  $bcc     = read_addr(PARAM_BCC);
  $return  = read_addr(PARAM_RETURN);
  $from    = read_addr(PARAM_FROM);
  $replyto = read_addr(PARAM_REPLYTO);

# read remaining parameters
  $mailserver  = read_param(PARAM_SERVER);
  $timeout     = read_param(PARAM_TIMEOUT);
  $subject     = read_param(PARAM_SUBJECT);
  $priority    = read_param(PARAM_PRIORITY);
  $verify      = read_param(PARAM_VERIFY);
  $debug       = read_param(PARAM_DEBUG);
  $body        = read_param(PARAM_BODY);

  $url_success = read_param(PARAM_SUCCESS); if ($url_success) { $url_success =~ s/\*/$domain/ }
  $url_error   = read_param(PARAM_ERROR);   if ($url_error)   { $url_error   =~ s/\*/$domain/ }

# validate sensitive parameters
  if ($debug) { $debug = 1 } else { $debug = 0 }
  if (!$timeout  or ($timeout  =~ /\D/)) { $timeout  = '' }
  if (!$priority or ($priority =~ /\D/)) { $priority = '' } elsif ($priority > 5) { $priority = 5  }

# supply required defaults
  unless ($timeout) { $timeout = DEFAULT_TIMEOUT }
  unless ($subject) { $subject = PROGRAM_NAME }
  unless ($return)  { $return  = '' }

# Replace semicolons with commas in cc/bcc lists.
  if ($cc)  { $cc  =~ s/;/,/g }
  if ($bcc) { $bcc =~ s/;/,/g }

# Check for error conditions. Done last to allow all data to be processed for debugging. 
  unless ($mailserver) { raise_ECustom('mailserver must be specified in .params file.') }
  unless ($to)         { raise_ECustom('To: address missing.') }

  if ($referrer) { # check against the browser referrer - fail if they don't match }
    my $ref = $ENV{'HTTP_REFERER'}; $ref = extract_domain($ref);

    if ((length($ref) != length($referrer))
    or  ($ref !~ /$referrer/i )) { raise_ECustom('Invalid referrer') }
  }
}

sub clean_addr # ($address)
{ my $addr = shift; unless ($addr) { return }

  $addr =~ s/".*"//g;  # delete quoted text - the display name
  $addr =~ s/[< >]//g; # delete spaces and unwanted '<','>' chars

  return $addr;
}

sub smtp_to # ($address)
{ my $addr   = shift; $addr = clean_addr($addr);
  my $result = 0;

  if ($addr) {
    $result = (!$verify or $smtp->verify($addr)) and $smtp->to($addr);
    if ($result) { $accept_addrs = add_line($accept_addrs,$addr); $accept_count++ }
            else { $reject_addrs = add_line($reject_addrs,$addr); $reject_count++ } 
  }

  return $result;
}

sub smtp_cc # ($ccAddressList)
{ my $cc = shift; unless ($cc) { return }
  my @cc = split(',', $cc);
  my $result = 1;

  foreach $cc (@cc) { $result = (smtp_to($cc) and $result) }

  return $result;
}

sub pad_eq # ($str)
# Place spaces around the first '=' char if not already present.
{ my $str = shift;
  my $i   = index($str,'=');
  if ($i > -1) {
    my $len = length($str);
    if (($len > $i + 1) and (substr($str,$i + 1,1) ne ' ')) { $str =~ s/=/= / }
    if (($i   > 0)      and (substr($str,$i - 1,1) ne ' ')) { $str =~ s/=/ =/ }
  }
  return $str
}

sub write_mail # ($prefix,$data,$isreply)
{ my $prefix  = shift;
  my $data    = shift;
  my $isreply = shift;

# If a prefix is specified but no data, return.
  if ($prefix and !$data) { return }

  my $line = "$prefix"."$data";

  if ($isreply or $debug) { push(@reply,$line) }

  unless (defined($smtp)) { return }

  $line = $line."\n";

  unless ($smtp->datasend($line)) { raise_ECustom('WRITE') }
}

sub write_maildata # ($lines)
# splits $lines if it contains \n.
# calls write_mail to send lines individually. 
{ my $tmp = shift; unless ($tmp) { return }

  my @lines = split(/\n/,$tmp);
  foreach $tmp (@lines) { write_mail('',$tmp,1) }
}

sub write_mailparams # ($params)
# $params is a string of data delimited by '&' chars.
{ my $params = shift; unless ($params) { return }
  my @params = split('&',$params);
  my $param;
  foreach $param (@params) {
    $param = url_decode($param,1);

#   If multiple lines need be written, place a linebreak after the '=' char
#   and add extra linebreaks at start and end of data
#   Typically, the source of multi-line data is a TEXTAREA control.
    if ($param =~ /\n/) {
      $param =~ s/=/=\n/;
      $param = "\n".$param."\n ";
    }

#   $param =~ s/_*=/=/;      # strip underscores directly before '=' char

    $param = pad_eq($param); # add spaces around '=' char if not present already

    write_maildata($param);
  }
}

sub create_mail {
# Create mail object.
# Optional parameters have been commented out. If any are included, the order MUST be preserved.

  my $record; if ($debug and $logfile) { $record = 1 } else { $record = 0 }

  $smtp = Net::SMTP->new($mailserver,
#                        'Hello'     => $domain,
#                        'LocalAddr' => ?????,
#                        'LocalPort' => 25,
                         'Timeout'   => $timeout,
                         'Debug'     => $record);

  unless(defined($smtp)) {
    raise_ECustom("CREATE - '$mailserver' may be invalid as the ".PARAM_SERVER.' value.')
  }

  eval {

#   ****************** Authentication *******************
#
#   If authentication is required, try replacing username
#   and password below. Also remove the leading '#' char.
#   The single quotes ('') are required.
#   Also refer to on online help at http://www.skaro.net
#   and/or downloaded documentation.
# 
#   unless($smtp->auth('username','password')) { raise_ECustom('AUTHENTICATION') }
#
#   THIS CODE IS UNTESTED. BEHAVIOUR WILL DEPEND ON
#   SERVER CONFIFIGURATION AND PERL VERSION.
#
#   *****************************************************

    unless ($smtp->mail($return)) { raise_ECustom('OPEN') }

#   Set the recipients
    smtp_to($to);  # set the primary address
    smtp_cc($cc);  # set the published copy addresses
    smtp_cc($bcc); # set the unpublished copy addresses

#   Check at least one recipient was accepted
    unless ($accept_count) { raise_ECustom('RECIPIENT(S) REJECTED') }

#   Set highest priority if any recipient was rejected.
#   The reject list is appended to the email later.
    if ($reject_count) { $priority = 1 }

#   Prepare to send data - the header is part of this.
    unless ($smtp->data) { raise_ECustom('BEGIN') }

#   Calculate the subject header.
    my $sh = $subject; if ($ticketvalue) { $sh = "[#$ticketvalue] $sh" }

#   Calculate the date header.
    my $dt = time2str();

#   Create the header
    write_mail('To: ',$to);
    write_mail('Cc: ',$cc);
    write_mail('Reply-To: ',$replyto);
    write_mail('From: ',$from);
    write_mail('Date: ',$dt);
    write_mail('Subject: ',$sh);
    write_mail('X-Priority: ',$priority);

#   Terminate the header block with the program identifier and extra linefeed.
    my $tmp = PROGRAM_NAME.' '.PROGRAM_VERSION.', '.PROGRAM_URL;
    write_mail('X-Mailer: ',"$tmp");
    write_mail('','');

#   Write the mail body. It's also displayed to the user to confirm what has been sent.
#   If a 'body=...' parameter is defined, use it, otherwise use the POST data.
    if ($body) { write_maildata($body) }
    else { @inputdata = <STDIN>;
           chomp(@inputdata);
           foreach $tmp (@inputdata) { write_mailparams($tmp) }
    }

#   If one or more recipients were rejected, append a reject list to the email.
    if ($reject_count) { $smtp->datasend("\n\n## ERROR: RECIPIENTS REJECTED ##\n$reject_addrs\n") }

    unless ($smtp->dataend) { raise_ECustom('CLOSE') };

  }; # EVAL

  handle_exception($@);

  unless ($smtp->quit) { raise_ECustom('QUIT') }; 
}

sub tohtml # ($line)
# Convert string to be printed in html page.
{ my $line = shift;

  if ($line) {
    $line =~ s/&/&amp\;/g;   # replace ampersands
    $line =~ s/</&lt\;/g;    # less than
    $line =~ s/>/&gt\;/g;    # greater than
    $line =~ s/\"/&quot\;/g; # quotes
  }

  return $line; 
}

sub print_html # ($line)
{ my $line = shift; $line = tohtml($line); print "$line"; }

sub print_param # ($name,$value);
{ my $name  = shift;
  my $value = shift;

  unless (defined($value)) { $value = '[undefined]' }

  print_html("$name = $value\n");
}

sub print_fileparams
{ my %hash = %fileparams;
  my @keys = keys(%hash);
  my @vals = values(%hash);
  my $key;
  
  print "<H3>Parameters Supplied by File : $paramfile</H3>\n<PRE>";
  print "! = Url param disabled.\n";
  print "* = Default\n    Url addresses are limited to this domain,\n    other url params are disabled.\n";
  print "    If an address contains only a domain name,\n    the url address must omit the domain.\n\n";

  foreach $key (@keys) { print_html("$key = $hash{$key}\n") }

  print "</PRE>\n";
}

sub print_urlparams
{ my %hash = %urlparams;
  my @keys = keys(%hash);
  my @vals = values(%hash);
  my $key;
  
  print "<H3>Parameters Supplied by URL</H3>\n<PRE>";

  foreach $key (@keys) { print_html("$key = $hash{$key}\n") }

  print "</PRE>\n";
}

sub print_usedparams # used for debugging only
{ print "<H3>Parameter Values Used</H3>\n<PRE>";

  print_param('mailserver ',$mailserver);
  print_param('domain     ',$domain);
  print_param('referrer   ',$referrer);
  print_param('verify     ',$verify);      print_html("\n");

  print_param('to         ',$to);
  print_param('cc         ',$cc);
  print_param('bcc        ',$bcc);
  print_param('return     ',$return);
  print_param('from       ',$from);
  print_param('replyto    ',$replyto);     print_html("\n");

  print_param('ticketfile ',$ticketfile);
  print_param('ticketbase ',$ticketbase);
  print_param('ticketvalue',$ticketvalue); print_html("\n");

  print_param('subject    ',$subject);
  print_param('priority   ',$priority);
  print_param('timeout    ',$timeout);
  print_param('success    ',$url_success);
  print_param('error      ',$url_error);
  print_param('debug      ',$debug);
  print_param('body       ',$body);

  print "</PRE>\n";
}

sub print_inputdata
{ if ($#inputdata < 0) { return }

  print "<H3>Input Data</H3>\n<PRE>";

  my $tmp; foreach $tmp (@inputdata) { print_html($tmp); print"\n" }
  print "</PRE>\n";
}

sub print_envvar # ($name);
{ my $name  = shift;       unless ($name)           { return }
  my $value = $ENV{$name}; unless (defined($value)) { $value = '' }

  print_html("$name = $value\n");
}

sub print_envvars
{ print "<H3>Environment vars</H3>\n<PRE>";

  print_envvar('QUERY_STRING');
  print_envvar('SERVER_NAME');
  print_envvar('HTTP_REFERER');
  print "</PRE>\n";
}

sub print_SMTPconversation
{ my @data;

  print "<H3>SMTP Conversation</H3>\n<PRE>";

  if ($logfile) {
    if (open(STDIN, "<$logfile")) {
      @data = <STDIN>;
      chomp(@data);
      if ($#data < 0) { @data = ('[LOG FILE IS EMPTY]') }
    }
    else { @data = ('Unable to open log file.') }
  }
  else { @data = ('Unable to create log file.') }

  foreach (@data) { print_html("$_\n") }
  print "</PRE>\n";
}

sub print_recipients
{ print "<H3>Recipients</H3>\n<PRE>";
  if ($accept_count) { print "Accepted: $accept_count\n" }
  if ($reject_count) {
    print "Rejected: $reject_count\n";
    if ($debug) { print "REJECTS\n$reject_addrs" }
  }
  print "</PRE>\n";
}

sub print_reply {
  begin_reply;

  my ($class,$tmp);
  if ($exception) { $class = ' CLASS="ERROR"'; $tmp = 'Mail could not be sent' }
         else { $class = '';               $tmp = 'The following data has been sent' }
  
  print "<H2$class>$tmp</H2>\n<P$class>\n";

  if ($exception) {
    $tmp = $exception;
    $tmp =~ s/\n/<BR>\n/g;
    print "$tmp";

    my $faulturl = clean_addr($to);
    if ($faulturl) {
      $faulturl = "mailto:$faulturl?subject=FORM%20MAIL%20%3A%20FAULT";
      print "<BR>\n<A HREF=\"$faulturl\">Click here</A> to send mail and report fault.<BR>\n"
  }}
  else { if ($ticketvalue) { print("TICKET #$ticketvalue<BR><BR>\n") }
         foreach $tmp (@reply) {
           print_html($tmp);
           print "<BR>\n"
  }}

  print "</P>\n";

  print_recipients;

  if ($debug) {
    open(STDERR, ">&STDOUT"); # reconnect STDERR to STDOUT and then print the error file

    print "<H3>Perl Version</H3>\n<PRE>$]</PRE>\n";

    print_envvars;
    print_urlparams;
    print_fileparams;
    print_usedparams;
    print_inputdata;
    print_SMTPconversation;
  }
}

sub main {
  eval {
    get_params;

    if ($debug) {
      $logfile = SCRIPT_NAME.'.smtp-log';

#     divert the standard error stream to a log file to record the smtp conversation
      unless (open (STDERR,">$logfile")) { $logfile = '' }
    } 

#   send the email
    eval { create_mail };

    print_reply;

#   Ecustom errors are handled by print_reply, however, we must reraise other exceptions.
    if ($@ and !is_Ecustom($@)) { die }
  }; # EVAL

# Print error message, if any.
  handle_exception($@);

  end_reply;
}

############## PROGRAM BODY ###############

# copy the STDERR handle. The handle_exception function writes to STDEXCPT not STDERR
  open(STDEXCPT,">>&STDERR");

# divert warnings to the main exception handler.
# no warnings should ever arise but it's best to handle them properly if they do.
  $SIG{'__WARN__'} = sub { handle_exception($_[0]) };

  main;

################## END ####################