import sys
import os
import asyncio
import json
from getpass import getpass as passw

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from librus import Librus


async def main():
	print("---------------- Librus API Dumper ----------------")

	_user =					input("Librus Synergia login:        ")
	_pass =					passw("Librus Synergia password:     ")
	_full_dump =			input("Full API dump? [Y/n]:         ")
	
	_full_dump = _full_dump.strip().lower() not in ["n", "no", "false"]

	if _full_dump:
		print(f"Dumping full API...")
	else:
		_api_path =			input("Enter API path to be dumped:  ").strip()
		print(f"Dumping only '{_api_path}' from API...")

	librus = Librus(None)
	if not await librus.mktoken(_user, _pass):
		print("Wrong credentials.")
		sys.exit(1)

	res = (await librus.get_data(""))["Resources"]
	res_big = res.copy()
	i = 0

	if _full_dump:
		for x in res:
			i += 1
			l = len(res)
			print(f"[{str(round(i * 100 / l)).rjust(3)}%  {str(i).rjust(len(str(l)))}/{l}]  Requesting '{x}'")
			item = await librus.get_data(x)
			res_big[x] = item
	else:
		data = await librus.get_data(_api_path)
		if not data:
			print(f"Error: Couldn't find '{_api_path}' in API, exiting...")
			raise SystemExit
		res_big[_api_path] = data

	print("Saving data to JSON...")
	result = open("api_dump.json", "w")
	result.write(json.dumps(res_big, indent = 4))
	result.close()
	print("Done.")


asyncio.run(main())
