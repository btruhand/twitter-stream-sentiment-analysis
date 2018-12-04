import json
import pprint

pp = pprint.PrettyPrinter()

with open('test.json') as fd:
	for line in fd:
		json_data = json.loads(line)
		pp.pprint(json_data)
		input('Continue? (press enter)')