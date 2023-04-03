import shutil
import socket
import re
import platform
import os
import sys


# Some helper functions
def get_script_path():
	return os.path.dirname(os.path.realpath(sys.argv[0]))

def get_local_ip_adress() -> str:
	# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
	local_ip_address = s.getsockname()[0]
	return local_ip_address

def validate_ip_address(ip_address) -> bool:
	# This is a simple regex pattern to match a valid IPv4 address
	pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
	return re.match(pattern, ip_address)

def validate_port_number(port) -> bool:
	try:
		port = int(port)
		if port < 1 or port > 65535:
			return False
		else:
			return True
	except ValueError:
		return False


# Setup wizard
def setup_wizard() -> tuple:
	print("\nWelcome to the Librusik setup wizard!\n")
	print("Please select or enter the IP address you want to use:\n")


	local_ip_adress = get_local_ip_adress()
	localhost = '127.0.0.1'
	anyip = '0.0.0.0'

	# Ask for IP address
	print("0. Any: " + anyip + " (default, recommended for servers)")
	print("1. Localhost: " + localhost + " (recommended for desktop computers)")
	print("2. Local IP address: " + local_ip_adress)
	print("3. Enter custom IP address\n")
	
	while True:
		option = input("Select an option (0-3): ")
		if option == "0":
			ip_address = anyip
			break
		elif option == "1":
			ip_address = localhost
			break
		elif option == "2":
			ip_address = local_ip_adress
			break
		elif option == "3":
			ip_address = input("Enter custom IP address: ")
			break

		else:
			print("Invalid option. Please try again.")
	
	# Validate input
	while not validate_ip_address(ip_address):
		print("Invalid IP address format. Please try again.")
		ip_address = input("Enter custom IP address: ")

	print("Selected IP address:", ip_address, "\n")

	# Ask for port
	print("Please select or enter the port number you want to use.\n")
	print("1. Default port: 7777")
	print("2. Enter custom port number\n")
	
	while True:
		option = input("Select an option (1-2): ")
		if option == "1":
			port = 7777
			break
		elif option == "2":
			port = input("Enter custom port number: ")
			break
		else:
			print("Invalid option. Please try again.")

	# Validate input
	while not validate_port_number(port):
		print("Invalid port number. Please try again.")
		port = input("Enter port number: ")

	print("Selected port: ", port, "\n")
	if platform.system() == "Windows":
		print("\nDo you want librusik to start at startup?")
		while True:
			option = input("Select an option (y/n): ")
			if option == "y":
				startup = True
				break
			elif option == "n":
				startup = False
				break
			else:
				print("Invalid option. Please try again.")

		if startup:
			if platform.system() == "Windows":
				with open("librusik.py", "r") as librusik_src:
					with open("librusik.pyw", "w") as librusik_dest:
						librusik_dest.write(librusik_src.read())
				with open("librusik.bat", "w") as bat_script:
					bat_script.write(f"@echo off\ncd {get_script_path()}\n{sys.executable.split()[-1].replace('python', 'pythonw')} librusik.pyw\ngoto :eof")
				shutil.copyfile("librusik.bat", os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "librusik.bat"))
				print("After system restart Librusik will start at startup.")
	return ip_address, port
