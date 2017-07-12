#!/bin/python
# Python2.7 :(

#Info
#====
#	file: smb_config
# 	name: Samba Share Configurate

#	version: 1.00
# 		*version is major.minor format
# 		*major is update when new capability is added
# 		*minor is update on fixes & improvements

#History
#=======
# 	03Jan2017 v1.00
#		SSgt Czerwinski, Thomas J.
#		*Created

#Description
#===========
#	Assist user in creating and connecting to SMB shares

#Notes
#=====

from ConfigParser import RawConfigParser as ConfigParser
from menu import Menu


USE_TEST_PROFILE = False

if USE_TEST_PROFILE is True:
	SMB_CONF_FILE = './smb.conf'
	SHARE_ROOT = './share/'
	MOUNT_ROOT = './mnt/'

else:
	SMB_CONF_FILE = '/etc/samba/smb.conf'
	SHARE_ROOT = '/cvah/data/assess/'
	MOUNT_ROOT = '/mnt/'
		

# Restarts services to effect share changes
def restart_smb( menu ):
	print( 'Restarting SMB Service..' )
	menu.run_cmd( 'service smb stop' )
	menu.run_cmd( 'service smb start' )

	print( 'Restarting NMB Service..' )
	menu.run_cmd( 'service nmb stop' )
	menu.run_cmd( 'service nmb start' )


# Prints the share information, pulled from smb.conf
def view_smb( menu, include_vals=True ):
	conf = ConfigParser()
	conf.read( SMB_CONF_FILE )

	print( 'Shares' )
	print( '------' )

	for share in conf.sections():
		print( share )

		if include_vals is True:
			for kv in conf.items( share ):print( '\t{} = {}'.format( kv[0], kv[1] ) )
			print( '' )


	print( '------')


# Lists local shares, actively shared on this machine
def list_shares( menu ):
	result = menu.run_cmd( 'smbclient -L localhost &', wait_for_cmd=False )
	if result is None: return result


# Creates a new share entry in smb.conf and creates a directory for the share path
def create_new_share( menu ):
	conf = ConfigParser()
	conf.read( SMB_CONF_FILE )

	name = menu.prompt( "Please enter a 'share name' to create" )
	share_path = SHARE_ROOT + name

	print( 'Creating share directory in ' + share_path )
	menu.run_cmd( 'mkdir -p ' + share_path, print_stdout=False )
	# Find a better way
	menu.run_cmd( 'chmod 777 ' + share_path, print_stdout=False )

	conf.add_section( name )
	conf.set( name, 'path', share_path )
	conf.set( name, 'comment', menu.prompt( "Please enter a 'comment' for this share" ) )
	#conf.set( name, 'workgroup', 'WORKGROUP' )
	conf.set( name, 'read only', 'no' )
	conf.set( name, 'writeable', 'yes' )
	#conf.set( name, 'write list', 'assessor' )
	conf.set( name, 'create mask', '0644' )
	conf.set( name, 'directory mask', '0755' )
	conf.set( name, 'valid users', 'assessor' )
	
	print( "Please enter 'hosts allowed' access to this share" )
	print( "* hosts must be 'space separated'" )
	print( "* hosts are in 'x.x.x.x' format" )
	print( "* entire subnets end with a '.'( i.e. x.x.x. is /24 )" )

	conf.set( 'global', 'hosts allow', menu.prompt( '' ) + ' 127.' )

	conf.write( open( SMB_CONF_FILE, 'w' ) )

	restart_smb( menu )


# Deletes a share from smb.conf, but does not remove the share path. This way, the user can preserved data
def delete_share( menu ):
	conf = ConfigParser()
	conf.read( SMB_CONF_FILE )

	view_smb( menu, include_vals=False )
	
	print( "The share directory will not be deleted" )
	conf.remove_section( menu.prompt( "Please enter the 'share name' to remove" ) )

	conf.write( open( SMB_CONF_FILE, 'w' ) )

	restart_smb( menu )


# Initiates a remote smb connect, lists remote shares, and connects to remote shares
def connect_remote_share( menu ):
	ip	= menu.prompt( "Please enter the 'IP address' of the remote machine" )
	user	= menu.prompt( "Please enter a 'user' to authenticate as" )

	print( 'Aquiring list of shares from server..' )

	#cmd_result = menu.run_cmd( 'smbclient -L ' + ip + ' -U ' + user + ' &', wait_for_cmd=False )
	cmd_result = menu.run_cmd( 'smbclient -L ' + ip + ' &', wait_for_cmd=False )
	if cmd_result != None: return cmd_result

	name = menu.prompt( "What is the 'share name' you'd like to connect to?" )

	print( 'Creating share directory in ' + MOUNT_ROOT + name )
	menu.run_cmd( 'mkdir -p ' + MOUNT_ROOT + name, print_stdout=False )

	if menu.prompt( "Is the remote machine Win7? ( y or n )", yn=True, to_lower=True ) is True:
		print( 'Connecting to remote share..' )
		cmd_result = menu.run_cmd( 'mount -t cifs //' + ip + '/' + name + ' /mnt/' + name + ' -o username=' + user )
		if cmd_result != None: return cmd_result

	else:
		print( 'Connecting to remote share..' )
		cmd_result = menu.run_cmd( 'mount //' + ip + '/' + name + ' /mnt/' + name + ' -o username=' + user )
		if cmd_result != None: return cmd_result


	#restart_smb( menu )


# Create Menu by registering options, desctiptions, and hooks/handlers
menu = Menu()
menu.register_option( 'v', 'View smb.conf Shares', view_smb )
menu.register_option( 'l', 'List Current Shares', list_shares )
menu.register_option( 'n', 'New Local Share', create_new_share )
menu.register_option( 'd', 'Delete Local Share', delete_share )
menu.register_option( 'c', 'List & Connect to a Remote Share', connect_remote_share )
menu.register_option( 'r', 'Manual SMB & NMB Restart', restart_smb )

restart_smb( menu )

# Format smb.conf so it's compatable with the ConfigParser module used by this script
with open( SMB_CONF_FILE, 'r+' ) as file:
	trimmed_file = []

	for line in file: trimmed_file.append( line.lstrip() )

	file.seek( 0 )
	for line in trimmed_file:
		file.write( line )

	file.truncate()


# Present the menu to the user & enter main loop
while menu.present() != 'exit': 1==1



