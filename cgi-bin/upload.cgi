#!/usr/bin/perl --

# Installation Instructions
# http://www.perlservices.net/en/programs/psupload/users_guide.shtml

# To order a custom installation
# https://www.perlscriptsjavascripts.com/psinstallation.html

#################################################################### 
#
#	PS Upload
#	©2002, PerlServices.net
#
#	Requires: Perl5+
#	Created:  March 12, 2002
#	Author:   PerlServices
#	Version:  4.1
#	
#	This script / program is copyright material!
#
#################################################################### 
# Start PS Upload Configuration
#################################################################### 

# ================================================================ #
# Var: $send_mail_path
# ================================================================ #
# for unix/linux servers only. enter your server's sendmail path. 
# it usually looks something like : 
# /usr/sbin/sendmail    or 
# /usr/lib/sendmail

$send_mail_path = "/usr/sbin/sendmail";

# ================================================================ #
# Var: $smtp_path
# ================================================================ #
# for windows servers only. enter your server's mail program path.
# it usually looks something like : 
# mail.yourdomainname.com    or
# smtp.yourdomainname.com

# note: if you set a value in the next variable, it will be used in 
# place of the $send_mail_path . Leave blank if you uploaded this
# script to a linux, unix or mac type server with sendmail, qmail 
# or postfix installed

$smtp_path = "";

# if your SMTP server requires authentication, enter the email 
# account's username and password below 
$smtp_user = "";
$smtp_pass = "";

# ================================================================ #
# Var: $notify
# ================================================================ #
# if you would like to be notified of uploads, enter your 
# email address between the SINGLE quotes. if you do not wish 
# to be notified, leave this blank. only one e-mail address can 
# be set here

$notify = 'admin@ahoythere.co.nz';

# ================================================================ #
# Var: $adminName
# ================================================================ #
# your name. the name that appears in the To: header in the e-mail 
# sent to the address specified in the $notify variable. enter the
# name between the single quotes.

$adminName = 'Lemusa';

# ================================================================ #
# Var: $subject
# ================================================================ #
# the subject of the e-mail notification. if you have a  field in 
# your form named "subject" in lowercase, that will over-ride this

$subject = 'File Uploaded';

# ================================================================ #
# Var: $dir
# ================================================================ #
# enter your server's path (not your website address) to the 
# directory files will be uploaded to.
# note : this script does not auto-delete uploaded files. 
# consider one of our other scripts if auto-deletion is required
#
# on most unix/linux server $ENV{DOCUMENT_ROOT}/ points to the
# folder your homepage resides in. however, sometimes you need to 
# also add www or htdocs to the path
#
# on windows servers, start the path with the drive letter and
# separate each folder with two backslashes.
# e.g. $dir = "F:\\webpath\\wwwroot\\uploads
#
# if you get this wrong, the script will print the correct path

$dir = "$ENV{DOCUMENT_ROOT}/uploads";

# ================================================================ #
# Var: $folder
# ================================================================ #
# absolute URL (website address starting with http://) to folder 
# files will be uploaded to. this variable correlates to the 
# previous variable.

$folder = "http://www.ahoythere.co.nz/uploads";

# ================================================================ #
# Var: $max
# ================================================================ #
# maximum file size (in kilobytes) you will accept as an upload. 
# your host can, and often, does override this setting. if you 
# cannot upload very large files, contact your host. it's not the 
# the script, it's the server. this script has successfully uploaded
# files larger than the Windows XP operating system!
# 1024 kilobytes is equal to 1 megabyte

$max = 15120;

# ================================================================ #
# Var: $print_contents
# ================================================================ #
# set to 1 if you would like the contents of your upload directory 
# ($dir) printed after a successful upload. set to 0 if you do not 
# want filenames printed. note: this is ignored if redirecting the 
# submitter to another page upon successful submission

$print_contents = 0;

# ================================================================ #
# Var: $overwrite
# ================================================================ #
# if the name of the file being uploaded already exists in your 
# upload directory ($dir) and you DO NOT WANT it over-written, 
# set this variable to 0 (zero). the script will then automatically 
# rename the file by appending a unique number to it.
# if you DO WANT existing files to be over-written by the new upload,
# then set this variable to 1

$overwrite = 0;

# ================================================================ #
# Var: $domain
# ================================================================ #
# to ensure this script only processes forms that reside on your 
# website, enter your domain name in this variable. the http://www
# portion is not required and best not be used.
#
# this helps prevent "hi-jacking" of your form. a technique 
# practiced by hackers to have a program on their website or local 
# computer programatically send out spam.
#
# note: this security measure is not fool proof and can be easily 
# circumvented by hackers. additionally, some web surfers may 
# unknowingly have the "referrer" variable cloaked, in which case, 
# if you have this variable set, they will not be able to submit 
# your form.
#
# we suggest you make use of the next security measure: @recipients

$domain = "ahoythere.co.nz";

# ================================================================ #
# Var: $domain
# ================================================================ #
#
# if a file is successfully uploaded, enter a URL to redirect to.
# use an absolute website address, as in : 
# http://www.google.com
# leave this blank to have the default message printed.

$redirect = "http://www.ahoythere.co.nz/about.html";

# ================================================================ #
# Var: @types
# ================================================================ #
# enter the file extensions for the file types you will accept. 
# this script can upload any type of file. each file extension on 
# a new line, or enter "ALL" in uppercase, to accept all file types

@types = qw~

ALL
gif
jpg
jpeg
xls
pdf
doc
txt
tx

~;

####################################################################
#    END USER EDITS
####################################################################

$folder =~ s/(\/|\\)+$//ig;
$dir    =~ s/(\/|\\)+$//ig;

$OS = $^O; # operating system name
if($OS =~ /darwin/i) { $isUNIX = 1; }
elsif($OS =~ /win/i) { $isWIN = 1; }
else {$isUNIX = 1;}
	
if($isWIN){ $S{S} = "\\\\"; }
else { $S{S} = "/";} # seperator used in paths

$ScriptURL = "http://$ENV{'SERVER_NAME'}$ENV{'SCRIPT_NAME'}";

unless (-d "$dir"){ mkdir ("$dir", 0777); chmod(0777, "$dir"); }

unless (-d "$dir"){
	# if there still is no dir, the path entered by the user is wrong and the upload will fail
	&PrintHead; #print the header
	
	# get the Win root
	$ENV{PATH_INFO} =~ s/\//$S{S}/gi;
	$ENV{PATH_TRANSLATED} =~ s/$ENV{PATH_INFO}//i;
	
	print qq~
	<table width="600">
	<tr>
	<td>
	
	<font face="Arial" size="2">
	<b>The path you entered is incorrect.</b> You entered : "$dir"
	<p>
	Your root path is (UNIX): $ENV{DOCUMENT_ROOT}
	<p>
	Your root path is (WINDOWS): $ENV{PATH_TRANSLATED}
	<p>
	Your path should contain your root path followed by a slash followed by the 
	destination folder's name. If you are on a WINDOWS server, each slash should 
	be escaped. Eg. each seperator should look like this : \\\\
	<p>
	Sometimes, the root returned is not the full path to your web space. In this case
	you should either check with your host  or if you are using an FTP client such as 
	CuteFTP, change to the folder you are trying to upload to and look at the path you 
	have taken. You can see this just above the list of files on your server.
	You must use the same path in the \$dir variable.
	</font>
	
	</td>
	</tr>
	</table>
	~;
	
	&PrintFoot; # print the footer
	exit;
}

use CGI; # load the CGI.pm module
my $GET = new CGI; # create a new object
my @VAL = $GET->param; #get all form field names

foreach(@VAL){
	$FORM{$_} = $GET->param($_); # put all fields and values in hash 
}

my @files;
foreach(keys %FORM){
	if($_ =~ /^FILE/){
		push(@files, $_); # place the field NAME in an array
	}
}

if(!$VAL[0]){
	# no form fields
	&PrintHead; #print the header
	
	print qq~
	<table width="760">
	<tr>
	<td>
	
	<font face="Arial" size="2">
	This script must be called using a form. Your form should point to this script. Your form tag must contain the following attributes : 
	<p>
	&lt;form <font color="#FF0000">action</font>="$ScriptURL" <font color="#FF0000">method</font>="post" <font color="#FF0000">enctype</font>="multipart/form-data"> 
	<p>
	The <font color="#FF0000">method</font> must equal <font color="#FF0000">post</font> and the <font color="#FF0000">enctype</font> must equal <font color="#FF0000">multipart/form-data</font>. The <font color="#FF0000">action</font> has to point to this script (on your server). If you are reading this, copy and paste the example above. It has the correct values.
	</font>
	
	</td>
	</tr>
	</table>
	~;
	
	&PrintFoot; # print the footer
	exit;
}

# check domain
if($domain =~ /\w+/){
	if($ENV{HTTP_REFERER} !~ /$domain/i){
		&PrintHead; #print the header

		print qq~
		<table width="600">
		<tr>
		<td>

		<font face="Arial" size="2">
		Invalid referrer.
		</font>

		</td>
		</tr>
		</table>
		~;
	
		&PrintFoot; # print the footer
		exit;
	}
}

my $failed; # results string = false
my $selected; # num of files selected by user

#################################################################### 

#################################################################### 

foreach (@files){
	# upload each file, pass the form field NAME if it has a value
	if($GET->param($_)){
		
		# if the form field contains a file name &psjs_upload subroutine
		# the file's name and path are passed to the subroutine 
		$returned = &psjs_upload($_); 
		
		if($returned =~ /^Success/i){
			# if the $returned message begins with "Success" the upload was succssful
			# remove the word "Success" and any spaces and we're left with the filename   
			$returned =~ s/^Success\s+//;
			push(@success, $returned);
		} else {
			# else if the word "success" is not returned, the message is the error encountered. 
			# add the error to the $failed scalar
			$failed .= $returned;
		}
		$selected++; # increment num of files selected for uploading by user
	}
}

if(!$selected){
	# no files were selected by user, so nothing is returned to either variable
	$failed .= qq~No files were selected for uploading~;
}

# if no error message is return ed, the upload was successful

my ($fNames, $aa, $bb, @current, @currentfiles );

if($failed){
	&PrintHead;	
	
	print qq~
	<table align="center" width="600">
	<tr>
	<td><font face="Arial" size="2">
	
	One or more files <font color="#ff0000">failed</font> to upload. The reasons returned are: 
	<p>
	
	$failed
	~;
	
	if($success[0]){
		# send email if valid email was entered
		if(check_email($notify)){
			
			# enter the message you would like to receive
			my $message = qq~
			The following files were uploaded to your server :
			~; 
			
			$folder =~ s/(\/|\\)$//ig;
			foreach(@success){
				$message .= qq~
				$folder/$_	
				~;
			}
			
			if(&send_mail($notify, $adminName, $notify, $adminName, $subject, $message)){
				$VAR{emailsuccess} = qq~Sent~;
			}
		}
	
		print qq~
		<p>
		The following files were <font color="#ff9900" face="monotype corsiva">successfully</font> uploaded :
		<p>
		~;	
		foreach(@success){
			print qq~
			$_<p>~;
		}
	}
	
	print qq~
	</font></td>
	</tr>
	</table>
	~;
	
	&PrintFoot;	
	
} else {
	# upload was successful
	
	# add a link to the file
	$folder =~ s/(\/|\\)$//ig;
	
	# send email if valid email was entered
	if(check_email($notify)){
		
		# enter the message you would like to receive
		my $message = qq~
		The following files were uploaded to your server :
		~; 
		
		foreach(@success){
			$message .= qq~
			$folder/$_	
			~;
		}
		
		if(&send_mail($notify, $adminName, $notify, $adminName, $subject, $message)){
			$VAR{emailsuccess} = qq~Sent~;
		}
	}
	
	if($redirect){
		# redirect user
		print qq~Location: $redirect\n\n~;
	} else {
		# print success page
		
		&PrintHead;	
		
		print qq~
		<table align="center" width="500" bgcolor="#000000">
		<tr>
		<th><font face="monotype corsiva" size="4" color="#ff9900">Upload Complete</font></th>
		</tr>
		<tr>
		<td><font face="monotype corsiva" size="4" color="aeaeae">You successfully uploaded the following file... 
		<p>
		~;
		
		foreach(@success){
			print qq~
			$_<p>~;
		}
		
		print qq~
		</font></td>
		</tr>
		</table>
		<br>
		~;
		
		if($print_contents){
			print qq~
			<table align="center" width="500">
			<tr><td><font face="Arial" size="2"><b>Current files in folder</b></td></tr>
			<tr>
			<td valign="top">
			<font face="Arial" size="2">
			~;
			
			opendir(DIR, "$dir");
			@current = readdir(DIR);
			closedir(DIR);
			
			foreach(@current){
				unless($_ eq '.' || $_ eq '..' || -d qq~$dir/$_~){
					push(@currentfiles, $_);
				}
			}
			
			@currentfiles = sort { uc($a) cmp uc($b) } @currentfiles;
			
			for($aa = 0; $aa <= int($#currentfiles / 2); $aa++){
				print qq~
				<font color="#ff0000"><b>&#149;</b> 
				<a href="$folder/$currentfiles[$aa]" target="_blank">$currentfiles[$aa]</a></font><br>
				~;
			}
			
			print qq~</font></td><td valign="top"><font face="Arial" size="2">~;
			
			for($bb = $aa; $bb < @currentfiles; $bb++){
				print qq~
				<font color="#ff0000"><b>&#149;</b> 
				<a href="$folder/$currentfiles[$bb]" target="_blank">$currentfiles[$bb]</a></font><br>
				~;
			}
			
			
			print qq~
			</font></td>
			</tr>
			</table>~;
		}
		
		print qq~
<br>
~;
		
		&PrintFoot;	
	
	}
}

#################################################################### 

#################################################################### 

sub psjs_upload {

	my ( %VAR, $type_ok, $file_contents, $buffer, $destination,  ); # declare some vars

	my $file = $GET->param($_[0]); # get the FILE name. $_[0] is the arg passed
	
	$destination = $dir;
	
	my $limit = $max;
	$limit *= 1024; # convert limit from bytes to kilobytes
	
	# create another instance of the $file var. This will allow the script to play 
	# with the new instance, without effecting the first instance. This was a major 
	# flaw I found in the psupload script. The author was replacing spaces in the path
	# with underscores, so the script could not find a file to upload. He blammed the 
	# error on browser problems.
	my $fileName    = $file; 
	
	# get the extension
	my @file_type   = split(/\./, $fileName);
	# we can assume everything after the last . found is the extension
	my $file_type   = $file_type[$#file_type];
	
	# get the file name, this removes everything up to and including the 
	# last slash found ( be it a forward or back slash )
	$fileName =~ s/^.*(\\|\/)//;
	
	# remove all spaces from new instance of filename var 
	$fileName =~ s/\s+//ig;
	
	# check for any any non alpha numeric characters in filename (allow dots and dahses)
	$fileName =~ s/\./PsJsDoT/g;
	$fileName =~ s/\-/PsJsDaSh/g;
	if($fileName =~ /\W/){
		$fileName =~ s/\W/n/ig; # replace any bad chars with the letter "n"
	}
	$fileName =~ s/PsJsDoT/\./g;
	$fileName =~ s/PsJsDaSh/\-/g;
	
	$VAR{isPHP}    = 0;
	$VAR{allowPHP} = 0;
	# if $file_type matchs one of the types specified, make the $type_ok var true
	for($b = 0; $b < @types; $b++){
		if($types[$b] =~ /^php$/i){
			$VAR{allowPHP}++;
		}
		if($file_type =~ /^$types[$b]$/i){
			$type_ok++;
		}
		if($types[$b] eq "ALL"){
			$type_ok++; # if ALL keyword is found, increment $type_ok var.
		}
	}
	
	# if ok, check if overwrite is allowed
	if($type_ok){
		if(!$overwrite){ # if $overwite = 0 or flase, rename file using the checkex sub
			$fileName = check_existence($destination,$fileName);
		}
		# create a new file on the server using the formatted ( new instance ) filename
		if(open(NEW, ">$destination$S{S}$fileName")){
			$VAR{err} .= $!;
			if($isWIN){ binmode NEW; } else { chmod(0777, "$destination$S{S}$fileName"); }
			# start reading users HD 1 kb at a time.
			while (read($file, $buffer, 1024)){ 
				# print each kb to the new file on the server 
				print NEW $buffer; 
				if($buffer =~ /<\?php/i){
					$VAR{isPHP}++;
				}
			}
			# close the new file on the server and we're done
			close NEW;
		} else {
			# return the server's error message if the new file could not be created
			return qq~Error: Could not open new file on server. $!~;
		}

		# check limit hasn't just been overshot
		if(-s "$destination$S{S}$fileName" > $limit){ # -s is the file size
			unlink("$destination$S{S}$fileName"); # delete it if it's over the specified limit
			return qq~File exceeded limitations : $fileName~;
		}
		
		# deny sneaky PHPs
		if($VAR{isPHP}){
			unless($VAR{allowPHP}){
				unlink("$destination$S{S}$fileName");
				return qq~PHP content is not permitted : $fileName~;
			}
		}
	} else {
		return qq~Bad file type : $file_type~; 
	}
			
	# check if file has actually been uploaded, by checking the file has a size
	if(-s "$destination$S{S}$fileName"){
		return qq~Success $fileName~; #success 
	} else {
		# delete the file as it has no content
		unlink("$destination$S{S}$fileName");
		# user probably entered an incorrect path to file
		return qq~Upload failed : No data in $fileName. No size on server's copy of file. 
		Check the path entered. $VAR{err}~; 
	}
}

#################################################################### 

#################################################################### 

sub check_existence {
	# $dir,$filename,$newnum are the args passed to this sub
	my ($dir,$filename,$newnum) = @_;
	
	my (@file_type, $file_type, $exists, $bareName); 
	# declare some vars we will use later on in this sub always use paranthesis 
	# when declaring more than one var! Some novice programmers will tell you 
	# this is not necessary. Tell them to learn how to program.
	
	if(!$newnum){$newnum = "0";} # new num is empty in first call, so set it to 0
	
	# read dir and put all files in an array (list)
	opendir(DIR, "$dir");
	@existing_files =  readdir(DIR);
	closedir(DIR);
	
	# if the filename passed exists, set $exists to true or 1
	foreach(@existing_files){
		if($_ =~ /^$filename$/i){
			$exists = 1;
		}
	}
	
	# if it exists, we need to rename the file being uploaded and then recheck it to 
	# make sure the new name does not exist
	if($exists){
		$newnum++; # increment new number (add 1)

		# get the extension
		@file_type   = split(/\./, $filename); # split the dots and add inbetweens to a list
		# put the first element in the $barename var
		$bareName    = $file_type[0]; 
		# we can assume everything after the last . found is the extension
		$file_type   = $file_type[$#file_type]; 
		# $#file_type is the last element (note the pound or hash is used)
		
		# remove all numbers from the end of the $bareName
		$bareName =~ s/\d+$//ig;
		
		# concatenate a new name using the barename + newnum + extension 
		$filename = $bareName . $newnum . '.' . $file_type;
		
		# reset $exists to 0 because the new file name is now being checked
		$exists = 0;
		
		# recall this subroutine
		&check_existence($dir,$filename,$newnum);
	} else {
		# the $filename, whether the first or one hundreth call, now does not exist
		# so return the name to be used
		return ($filename);
	}
}

#################################################################### 

#################################################################### 

sub send_mail {
	my ( %VAR, @atts ); 
	
	$VAR{sndrEml} = shift;
	$VAR{sndrNme} = shift;
	$VAR{rcvrEml} = shift;
	$VAR{rcvrNme} = shift;
	$VAR{subject} = shift;
	$VAR{message} = shift;
	$VAR{ccrcEml} = shift;
	$VAR{ccrcNme} = shift;
	$VAR{attPths} = shift;
	
	$VAR{Host}    = &gethostname;
	$CONFIG{mail_format} = 2;
	
	$VAR{message} .= qq~\n\nIP Address: $ENV{REMOTE_ADDR}\nHost Node: $VAR{Host}\nUser Agent: $ENV{HTTP_USER_AGENT}~;
	
	if($smtp_path =~ /\w+/){
		$CONFIG{mailprogram} = $smtp_path;
		$CONFIG{mailuser}    = $smtp_user;
		$CONFIG{mailpass}    = $smtp_pass;
		
		$VAR{res} = &send_mail_NT(
			$VAR{sndrEml}, 
			$VAR{sndrNme}, 
			$VAR{rcvrEml}, 
			$VAR{rcvrNme},
			$VAR{subject}, 
			$VAR{message}, 
			$VAR{ccrcEml}, 
			$VAR{ccrcNme}, 
			$VAR{attPths}
		);
		
		return $VAR{res};
	} else {
		$CONFIG{mailprogram} = $send_mail_path;
	}
	
	$VAR{CRLF}    = "\n";
	
	$VAR{message} =~ s/\r//ig;
	$VAR{message} =~ s/\n{3,300}/$VAR{CRLF}$VAR{CRLF}/ig;
	$VAR{message} =~ s/\n/$VAR{CRLF}/ig;
	$VAR{attPths} =~ s/\s+//ig;
	
	$VAR{HTMLmess} = $VAR{message};
	$VAR{TEXTmess} = $VAR{message};
	if($CONFIG{mail_format} == 2){
		$VAR{TEXTmess} =~ s/\&quot;/\"/g;
		$VAR{TEXTmess} =~ s/\&lt;/\</ig;
	}
	$VAR{files}    = qq~~;
	$VAR{hasAtts}  = 0;
	
	$VAR{sndrNme} =~ s/\&lt;/\</ig;
	$VAR{rcvrNme} =~ s/\&lt;/\</ig;
	$VAR{subject} =~ s/\&lt;/\</ig;
	$VAR{ccrcNme} =~ s/\&lt;/\</ig;
	
	$VAR{sndrNme} =~ s/\<.*?>//ig;
	$VAR{rcvrNme} =~ s/\<.*?>//ig;
	$VAR{subject} =~ s/\<.*?>//ig;
	$VAR{ccrcNme} =~ s/\<.*?>//ig;
	
	$VAR{bound1}   = qq~----=_NextPart_P_115Dream~; # printable
	$VAR{bound2}   = qq~----=_NextPart_A_SubHB~; # attachments
	$VAR{bound3}   = qq~----=_NextPart_E_SlowTrain~; # embded
	
	$VAR{fm} = $VAR{sndrNme} =~ /\w+/ ? qq~$VAR{sndrEml} ($VAR{sndrNme})~ : $VAR{sndrEml};
	$VAR{to} = $VAR{rcvrNme} =~ /\w+/ ? qq~$VAR{rcvrEml} ($VAR{rcvrNme})~ : $VAR{rcvrEml};
	$VAR{cc} = $VAR{ccrcNme} =~ /\w+/ ? qq~$VAR{ccrcEml} ($VAR{ccrcNme})~ : $VAR{ccrcEml};
	
	if(open(M, qq~|$CONFIG{mailprogram} -t ~)){
		print M qq~From: $VAR{fm}$VAR{CRLF}~;
		print M qq~To: $VAR{to}$VAR{CRLF}~;
		print M qq~CC: $VAR{cc}$VAR{CRLF}~ if $VAR{ccrcEml};
		print M qq~Subject: $VAR{subject}$VAR{CRLF}~;
		print M qq~MIME-Version: 1.0$VAR{CRLF}~;
		
		if($CONFIG{mail_format} == 1){
			print M qq~$VAR{fileHeaders}~;
			print M qq~$VAR{embedHeaders}~;
			
			print M qq~Content-Type: multipart/alternative;$VAR{CRLF}~;
			print M qq~\tboundary="$VAR{bound1}"$VAR{CRLF}$VAR{CRLF}$VAR{CRLF}~;
			print M qq~--$VAR{bound1}$VAR{CRLF}~;
			print M qq~Content-Type: text/plain;$VAR{CRLF}~;
			print M qq~Content-Transfer-Encoding: 7bit$VAR{CRLF}$VAR{CRLF}~;
			print M qq~$VAR{TEXTmess}$VAR{CRLF}$VAR{CRLF}~;
			
			print M qq~--$VAR{bound1}$VAR{CRLF}~;
			print M qq~Content-Type: text/html; $VAR{charset2}$VAR{CRLF}$VAR{CRLF}~;
			
			print M qq~$VAR{HTMLmess}$VAR{CRLF}~;
			
			print M qq~$VAR{CRLF}$VAR{CRLF}--$VAR{bound1}--$VAR{files}~;
		} else {
			print M qq~$VAR{fileHeaders}~;
			print M qq~Content-Type: text/plain;$VAR{CRLF}~;
			print M qq~Content-Transfer-Encoding: 7bit$VAR{CRLF}$VAR{CRLF}~;
			print M qq~$VAR{TEXTmess}$VAR{CRLF}$VAR{CRLF}$VAR{files}~;
		}
		
		close M; return 1;
	} else { return; }
}

#################################################################### 

#################################################################### 

sub send_mail_NT {
	my ( %VAR, @atts ); 
	
	$VAR{sndrEml} = shift;
	$VAR{sndrNme} = shift;
	$VAR{rcvrEml} = shift;
	$VAR{rcvrNme} = shift;
	$VAR{subject} = shift;
	$VAR{message} = shift;
	$VAR{ccrcEml} = shift;
	$VAR{ccrcNme} = shift;
	$VAR{attPths} = shift;
	
	use Socket;
	
	$VAR{CRLF}    = "\015\012";
	$VAR{debug}   = 0;
	
	if($VAR{debug}){
		#BEGIN { 
		#	$| = 1;
		#	open (STDERR, ">&STDOUT");
		#	print qq~Content-type: text/html\n\n<pre>~;
		#}
	}

	$VAR{message} =~ s/\r+//ig;
	$VAR{message} =~ s/\n{3,300}/$VAR{CRLF}$VAR{CRLF}/ig;
	$VAR{message} =~ s/\n/$VAR{CRLF}/ig;
	$VAR{attPths} =~ s/\s+//ig;
	
	$VAR{HTMLmess} = $VAR{message};
	$VAR{TEXTmess} = $VAR{message};
	if($CONFIG{mail_format} == 2){
		$VAR{TEXTmess} =~ s/\&quot;/\"/g;
		$VAR{TEXTmess} =~ s/\&lt;/\</ig;
	}
	$VAR{files}    = qq~~;
	$VAR{hasAtts}  = 0;
	
	$VAR{bound1}   = qq~----=_NextPart_P_115Dream~; # printable
	$VAR{bound2}   = qq~----=_NextPart_A_SubHB~; # attachments
	$VAR{bound3}   = qq~----=_NextPart_E_SlowTrain~; # embded
	
	$VAR{fm} = $VAR{sndrNme} =~ /\w+/ ? qq~$VAR{sndrEml} ($VAR{sndrNme})~ : $VAR{sndrEml};
	$VAR{to} = $VAR{rcvrNme} =~ /\w+/ ? qq~$VAR{rcvrEml} ($VAR{rcvrNme})~ : $VAR{rcvrEml};
	$VAR{cc} = $VAR{ccrcNme} =~ /\w+/ ? qq~$VAR{ccrcEml} ($VAR{ccrcNme})~ : $VAR{ccrcEml};
	
	$* = 1; # Set regex to handle multiple line strings
	$VAR{SMTPserver} = $CONFIG{mailprogram};
	$VAR{SMTPport}   = 25;
	$VAR{Stream}     = $] > 5 ? SOCK_STREAM : 1;
	$VAR{AFinet}     = $] > 5 ? AF_INET : 2;
	
	$VAR{protocol}   = (getprotobyname('tcp'))[2];
	$VAR{hostName}   = (gethostbyname($VAR{SMTPserver}))[4];
	
	$VAR{bindSock}   = pack('S n a4 x8', $VAR{AFinet}, 0, $VAR{hostName});
	$VAR{connSock}   = pack('S n a4 x8', $VAR{AFinet}, $VAR{SMTPport}, $VAR{hostName});
	
	unless(socket(M, $VAR{AFinet}, $VAR{Stream}, $VAR{protocol})){
		if($VAR{debug}){ print qq~No socket established\n\n~; } return;
	}
	
	bind(M, $VAR{bindSock});
	
	unless(connect(M, $VAR{connSock})){
		if($VAR{debug}){ print qq~No connection established\n\n~; } return;
	}
	
	$VAR{selected} = select(M); $| = 1; select($VAR{selected});
	
	select(undef, undef, undef, 1);
	sysread(M, $_, 1024);
	if($VAR{debug}){ print qq~Connection accepted:$_ \n\n~; }
	
	print M qq~HELO $VAR{SMTPserver}$VAR{CRLF}~;
	sysread(M, $_, 1024);
	if($VAR{debug}){ print qq~HELO:$_ \n\n~; }
	if(!/^\s*250/){ if($VAR{debug}){ print qq~HELO failed\n\n~;} return; }
	
	# authenticate ourselves?
	if($CONFIG{mailuser} =~ /\w+/ && $CONFIG{mailpass} =~ /\w+/){
		$VAR{SMTPuser} = $CONFIG{mailuser};
		$VAR{SMTPpass} = $CONFIG{mailpass};
		
		$VAR{length} = $VAR{SMTPuser};
		$VAR{encoded} = substr(pack('u57', $VAR{SMTPuser}), 1); chop($VAR{encoded});
		$VAR{encoded} =~ tr| -_`|A-Za-z0-9+/A|;
		$VAR{buff} = (3 - ($VAR{length} % 3)) % 3;
		substr($VAR{encoded}, -$VAR{buff}, $VAR{buff}) = '=' x $VAR{buff};
		$VAR{SMTPuser} = $VAR{encoded};
		
		$VAR{length} = $VAR{SMTPpass};
		$VAR{encoded} = substr(pack('u57', $VAR{SMTPpass}), 1); chop($VAR{encoded});
		$VAR{encoded} =~ tr| -_`|A-Za-z0-9+/A|;
		$VAR{buff} = (3 - ($VAR{length} % 3)) % 3;
		substr($VAR{encoded}, -$VAR{buff}, $VAR{buff}) = '=' x $VAR{buff};
		$VAR{SMTPpass} = $VAR{encoded};
		
		print M qq~AUTH LOGIN$VAR{CRLF}~;
		sysread(M, $_, 1024);
		if($VAR{debug}){ print qq~AUTH LOGIN: $_\n\n~; }
		
		print M qq~$VAR{SMTPuser}$VAR{CRLF}~;
		sysread(M, $_, 1024);
		if($VAR{debug}){ print qq~Auth Username: $_\n\n~; }
		
		print M qq~$VAR{SMTPpass}$VAR{CRLF}~;
		sysread(M, $_, 1024);
		if($VAR{debug}){ print qq~Auth Password: $_\n\n~; }
	}
	
	print M qq~MAIL FROM:$VAR{sndrEml}$VAR{CRLF}~;
	sysread(M, $_, 1024);
	if($VAR{debug}){ print qq~MAIL FROM:$_\n\n~; }
	if(!/[^0-9]*250/){ if($VAR{debug}){ print qq~Denied.\n\n~; } return; }
	
	print M qq~RCPT TO:$VAR{rcvrEml}$VAR{CRLF}~;
	sysread(M, $_, 1024); /[^0-9]*(\d\d\d)/;
	if($VAR{debug}){ print qq~RCPT TO:$_\n\n~; }
	if(!/[^0-9]*250/){ if($VAR{debug}){ print qq~Denied. Auth required?\n\n~; } return; }
	
	if($VAR{ccrcEml}){
		print M qq~RCPT TO:$VAR{ccrcEml}$VAR{CRLF}~;
		sysread(SMTP, $_, 1024); /[^0-9]*(\d\d\d)/;
		if($VAR{debug}){ print qq~RCPT TO CC:$_\n\n~; }
		if(!/[^0-9]*250/){ if($VAR{debug}){ print qq~Denied. Auth required?\n\n~; } return; }
	}
	
	print M qq~DATA$VAR{CRLF}~;
	sysread(M, $_, 1024);
	if($VAR{debug}){ print qq~Ready to send DATA:$_\n\n~; }
	if(!/[^0-9]*354/){ if($VAR{debug}){ print qq~Denied.\n\n~; } return; }
	
	print M qq~From: $VAR{fm}$VAR{CRLF}~;
	print M qq~To: $VAR{to}$VAR{CRLF}~;
	print M qq~CC: $VAR{cc}$VAR{CRLF}~ if $VAR{ccrcEml};
	print M qq~Subject: $VAR{subject}$VAR{CRLF}~;
	print M qq~MIME-Version: 1.0$VAR{CRLF}~;
	
	if($CONFIG{mail_format} == 1){
		print M qq~$VAR{fileHeaders}~;
		print M qq~$VAR{embedHeaders}~;
		
		print M qq~Content-Type: multipart/alternative;$VAR{CRLF}~;
		print M qq~\tboundary="$VAR{bound1}"$VAR{CRLF}$VAR{CRLF}$VAR{CRLF}~;
		print M qq~--$VAR{bound1}$VAR{CRLF}~;
		print M qq~Content-Type: text/plain;$VAR{CRLF}~;
		print M qq~Content-Transfer-Encoding: 7bit$VAR{CRLF}$VAR{CRLF}~;
		print M qq~$VAR{TEXTmess}$VAR{CRLF}$VAR{CRLF}~;
		
		print M qq~--$VAR{bound1}$VAR{CRLF}~;
		print M qq~Content-Type: text/html; $VAR{charset2}$VAR{CRLF}$VAR{CRLF}~;
		
		print M qq~$VAR{HTMLmess}$VAR{CRLF}~;
		
		print M qq~$VAR{CRLF}$VAR{CRLF}--$VAR{bound1}--$VAR{files}~;
	} else {
		print M qq~$VAR{fileHeaders}~;
		print M qq~Content-Type: text/plain;$VAR{CRLF}~;
		print M qq~Content-Transfer-Encoding: 7bit$VAR{CRLF}$VAR{CRLF}~;
		print M qq~$VAR{TEXTmess}$VAR{CRLF}$VAR{CRLF}$VAR{files}~;
	}
	
	print M qq~$VAR{CRLF}.$VAR{CRLF}~;
	sysread(M, $_, 1024);
	if($VAR{debug}){ print qq~Message ended:$_\n\n~; }
	if(!/[^0-9]*250/){ if($VAR{debug}){ print qq~Message failed.\n\n~; } return; }
	
	if(!shutdown(M, 2)){
		if($VAR{debug}){ print qq~Shutdown failed:$_\n\n~; } return;
	} else { return 1; }
}

#################################################################### 

#################################################################### 

sub PrintHead {
	print qq~Content-type: text/html\n\n~;
	print qq~
	<html>
	<title>PerlServices.net Free upload utility</title>
	<body bgcolor="#000000">
	~;
}

#################################################################### 

#################################################################### 

sub PrintFoot {
	print qq~
	</body>
	</html>
	~;
}

#################################################################### 

#################################################################### 

sub check_email {
	my($fe_email) = $_[0];
	if($fe_email) {
		if(($fe_email =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)|(\.$)/) ||
		($fe_email !~ /^.+@\[?(\w|[-.])+\.[a-zA-Z]{2,3}|[0-9]{1,3}\]?$/)) {
			return;
		} else { return(1) }
	} else {
		return;
	}
}

#####################################################################

#####################################################################

sub gethostname {
	$ipnum = $ENV{'REMOTE_ADDR'};
	@digits = split (/\./, $ipnum);
	$address = pack ("C4", @digits);
	$host = gethostbyaddr ($address, 2);

	return ($host);
}
