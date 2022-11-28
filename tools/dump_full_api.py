import sys
import os
import asyncio
import json
import getpass

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from librus import Librus


async def main():
	print("---------------- Librus API Dumper ----------------")
	_user = input("Librus Synergia login:     ")
	_pass = getpass.getpass("Librus Synergia password:  ")

	librus = Librus(None)

	if not await librus.mktoken(_user, _pass):
		print("Wrong credentials.")
		sys.exit(1)

	res = (await librus.get_data(""))["Resources"]
	res_big = res.copy()
	i = 0

	for x in res:
		i += 1
		l = len(res)
		print(f"[{str(round(i * 100 / l)).rjust(3)}%  {str(i).rjust(len(str(l)))}/{l}]  Requesting '{x}'")
		item = await librus.get_data(x)
		res_big[x] = item

	print("Saving data to JSON...")
	result = open("api_dump.json", "w")
	result.write(json.dumps(res_big))
	result.close()
	print("Done.")


asyncio.run(main())
