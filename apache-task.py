#!/usr/bin/python
import sys 
import platform 
import os
from subprocess import call
from optparse import OptionParser
import optparse




#Arguments for command line
parser = OptionParser(usage = "usage: %prog [options] arg1 arg2", version="%prog 0.01", 
  			description="Please be aware this script will OVERRIDE files if they exist! Supported OS's are 'Ubuntu', 'CentOS' and 'Red Hat Enterprise Linux Server'")
parser.add_option("-d", "--domain", 
				action="store", type="string", dest="user_domain",
                help="Domain to use (Without WWW)", metavar="example.com")
parser.add_option("-r", "--docroot",
                action="store", type="string", dest="user_docroot",
                help="Document Root for virtual host", metavar="/var/www/vhosts/example.com")
parser.add_option("--ip",
                action="store", type="string", dest="user_ip",
                help="IP Address for virtual host", metavar="192.168.0.1")
parser.add_option("--ssl",
                action="store_true", dest="user_ssl",
                help="Add SSL to virtual host", metavar="")

(opts, args) = parser.parse_args()


#Platform check
def support_platforms():
	supportedOS = ['Ubuntu', 'CentOS', 'Red Hat Enterprise Linux Server']
	(distro, version, codename) = platform.linux_distribution()
	checker = [X for X in supportedOS if distro in X]
	if checker == []:
		print '================================================================================='
		print '|                System Check has return an unsupported OS                      |'
		print '|Supported OS\'s: ', 
		print supportedOS,
		print '      |'
		print '|OS Found: ', 
		print distro + ' ' + version,
		print  '                                                       |'
		print '================================================================================='
		raise SystemExit
	else:
		return checker

#Check and Create folder(s)
def does_it_exist(dir_path):
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
		return 'Created: ' + dir_path
	else:
		return 'Folder exists: ' + str(dir_path)


#Create SSL Files
def ssl_files(filetype):
	ssl_input = [] 
	entry = raw_input("Please paste the " + filetype + " file then type 'done' on its own line to complete entry: \n") 
	while entry != "done":
    		ssl_input.append(entry) 
    		entry = raw_input("") 

	ssl_input = '\n'.join(ssl_input) 
	if filetype is 'crt':
		fileis = 'certs'
		fileext = '.crt'
	elif filetype is 'key':
		fileis = 'private'
		fileext = '.key'

	does_it_exist('/etc/pki/tls/' + fileis + '/')
	opentestfile = open('/etc/pki/tls/' + fileis + '/' + opts.user_domain + fileext, 'w')
	opentestfile.write(ssl_input)
	opentestfile.close()

#Run Platform Checker
system_checked = support_platforms()


#Define System differences
if system_checked == ['Ubuntu']:
	etc_conf = '/etc/apache2/sites-available/'
	etc_conf_exist = does_it_exist(etc_conf)
	log_loc = '/var/log/apache2/'
	log_loc_exist = does_it_exist(log_loc)
	conf_ext = ''
	apache_ex = '/etc/init.d/apache2'
	extra_command_1 = '/usr/sbin/a2ensite'
elif system_checked == (['Red Hat Enterprise Linux Server'] or ['CentOS']):
	etc_conf = '/etc/httpd/vhosts/'
	etc_conf_exist = does_it_exist(etc_conf)
	log_loc = '/var/log/httpd/'
	log_loc_exist = does_it_exist(log_loc)
	conf_ext = '.conf'
	apache_ex = '/etc/init.d/httpd'


#If no domain specified prompt
if opts.user_domain is None:
	opts.user_domain = raw_input("Enter the domain (without WWW): ")

#If no docroot specified use default
if opts.user_docroot is None:
	opts.user_docroot = '/var/www/vhosts/' + opts.user_domain + '/public_html'

#If no IP specified use all
if opts.user_ip is None:
	opts.user_ip = '*'

#If SSL not set then comment out SSL items
if opts.user_ssl is None:
	use_ssl = '#'
else:
	use_ssl = ''
	ssl_files('crt')
	ssl_files('key')


#Check docroot exists
doc_root_exist = does_it_exist(opts.user_docroot)

#vhost config file
vhost_conf = "<VirtualHost " + opts.user_ip + ":80>\n\
	ServerName " + opts.user_domain + "\n\
	ServerAlias www." + opts.user_domain + "\n\
	DocumentRoot " + opts.user_docroot + " \n\
	<Directory " + opts.user_docroot + ">\n\
		AllowOverride All\n\
	</Directory>\n\
	CustomLog " + log_loc + opts.user_domain + "-access_log common\n\
	ErrorLog " + log_loc + opts.user_domain + "-error_log\n\
</VirtualHost>\n\
\n\
\n\
" + use_ssl + " <VirtualHost " + opts.user_ip + ":443>\n\
" + use_ssl + " ServerName " + opts.user_domain + "\n\
" + use_ssl + " DocumentRoot " + opts.user_docroot + "\n\
" + use_ssl + " <Directory " + opts.user_docroot + ">\n\
" + use_ssl + "	AllowOverride All\n\
" + use_ssl + " </Directory>\n\
\n\
" + use_ssl + " CustomLog " + log_loc + opts.user_domain + "-ssl-access.log combined\n\
" + use_ssl + " ErrorLog " + log_loc + opts.user_domain + "-ssl-error.log\n\
\n\
" + use_ssl + " # Possible values include: debug, info, notice, warn, error, crit,\n\
" + use_ssl + " # alert, emerg.\n\
" + use_ssl + " LogLevel warn\n\
\n\
" + use_ssl + " SSLEngine on\n\
" + use_ssl + " SSLCertificateFile    /etc/pki/tls/certs/" + opts.user_domain + ".crt\n\
" + use_ssl + " SSLCertificateKeyFile /etc/pki/tls/private/" + opts.user_domain + ".key\n\
\n\
" + use_ssl + " <FilesMatch \"\.(cgi|shtml|phtml|php)$\">\n\
" + use_ssl + " 	SSLOptions +StdEnvVars\n\
" + use_ssl + " </FilesMatch>\n\
\n\
" + use_ssl + " BrowserMatch \"MSIE [2-6]\" \\\n\
" + use_ssl + "	nokeepalive ssl-unclean-shutdown \\\n\
" + use_ssl + "	downgrade-1.0 force-response-1.0\n\
" + use_ssl + " BrowserMatch \"MSIE [17-9]\" ssl-unclean-shutdown\n\
" + use_ssl + " </VirtualHost>\n"

#write vhost file
opentestfile = open(etc_conf + opts.user_domain + conf_ext, 'w')
opentestfile.write(vhost_conf)
opentestfile.close()

#If Ubuntu run a2ensite to enable site
if system_checked == ['Ubuntu']:
	call([extra_command_1, opts.user_domain])

#Reload apache
call([apache_ex, "reload"])



