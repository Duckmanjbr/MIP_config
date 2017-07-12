#!/bin/python
# Python2.7 :(

#Info
#====
#	file: menu.py
# 	name: Utility Menu Class

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
#	Menu class to facilitate creating terminal menus

#Notes
#=====

from collections import OrderedDict
from subprocess import Popen, PIPE, STDOUT


class Menu:
	def __init__( self ):
		self._options = OrderedDict( [( 'x', ( 'Exit', None ) )] )


	def register_option( self, selector, description, func ):
		if selector == 'x':
			print( "The 'x' selector is reserved for the exit function" )
			return 'fail'


		self._options[selector] = ( description, func )


	def present( self ):
		print( self )

		opt = raw_input()

		if opt in self._options:
			print( '===============================\n' )

			if opt == 'x': return 'exit'

			result = self._options[opt][1]( self )
			if result is not None: return result

		else:
			print( '[ ERR ] Invalid Option' )
			print( '===============================\n' )
			self.present()


	def  prompt( self, msg, yn=False, to_lower=False ):
		while True:
			print( msg )
			response = str( raw_input() )

			if to_lower is True: response = response.lower()

			if yn is True:
				if response == 'y':	return True
				if response == 'n':	return False
				else:
					print( "[ ERR ] Invalid Input( y or n only ).. Try again!" )

			else:
				if response != '': break

				print( "[ ERR ] No Input Provided.. Try again!" )


		return response


	def message( self, msg ): print( msg )

	def run_cmd( self, args, print_stdout=True, dump_on_error=True, wait_for_cmd=True ):
#		cmd = Popen( args, shell=True, stdout=PIPE, stderr=PIPE )
		cmd = Popen( args, shell=True, stdout=PIPE, stderr=STDOUT )	

		if wait_for_cmd is True: cmd.wait()
 
		if print_stdout is True:
			for line in cmd.stdout: print( line.decode() )


		if cmd.returncode > 0:
			if dump_on_error is True:
				for line in cmd.stdout: print( line.decode() )

		
			print( '[ CMD ERR ]\n' )
			return cmd.returncode


#		elif cmd.stderr:
#			print( '[ CMD COMPLETED W/ ERR ] The following errors were reported\n' )

#			for line in cmd.stderr: print( line.decode() )
			
#			abort = self.prompt( 'Would you like to abort( y or n )?', yn=True, to_lower=True )
#			if abort is True: return '[ ABORT ] By User\n'
		
#		else: print( '[ CMD OK ]\n' )



	def __str__( self ):
		msg =	'\n' \
			'SMB Share Configuration Options\n' \
			'===============================\n'

		for opt in self._options:
			msg += '{}	{}\n'.format( opt, self._options[opt][0] )


		msg += '-------------------------------'

		return msg

