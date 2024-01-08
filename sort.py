# ______________________________________________________________________________
#
#  Sort content (apps, games, themes) into another folder based on metadata
#  in the JSON index file
# ______________________________________________________________________________
#
import os, sys
import json, shutil

list = {}
rootdir = ''
outdir = ''

def sort(infile):
	with open(infile, 'r') as in_f:
		index = json.loads(in_f.read())

	with open("resolutions.json", 'r') as res_f:
		resolutions = json.loads(res_f.read())

	for (hash, item) in index.items():
		# /Applications/
		if 'MIDlet-Vendor' in item and item['MIDlet-Vendor'] == 'Nokia':
			if 'Nokia-MIDlet-Category' in item:
				type = item['Nokia-MIDlet-Category'] + 's'
			else:
				type = 'Applications'
		elif 'MIDlet-1' not in item:
			type = 'Themes'
		else:
			type = 'Third-party'
		if type not in list: list[type] = {'type': 'folder'}

		# /Applications/Snake EX2
		if 'MIDlet-Name' in item:
			title = item['MIDlet-Name']
		else:
			title = item['paths'][0].split('/')[-1].split('.nth')[0]
		if title not in list[type]: list[type][title] = {'type': 'folder'}

		# /Applications/Snake EX2/128x160_6070/
		modeltype = item['paths'][0].split('/')[2].split('_')[0]
		if modeltype in resolutions:
			model = resolutions[modeltype]
		else:
			raise KeyError(f"'{modeltype}' is not in resolutions.json")
		if model not in list[type][title]: list[type][title][model] = {'type': 'folder'}

		# Use a version subfolder for jars, no version for themes
		if 'MIDlet-Version' in item:
			# /Applications/Snake EX2/128x160_6070/1.1/
			version = item['MIDlet-Version']
			if version not in list[type][title][model]:
				list[type][title][model][version] = {'type': 'folder'}

			# /Applications/Snake EX2/128x160_6070/1.1/snake_en_fr_de_hu-HU_pl-PL_ro-RO.jar
			name = item['paths'][0].split('/')[-1]
			list[type][title][model][version][name] = {'type': 'file', 'path': item['paths'][0]}
		else:
			name = item['paths'][0].split('/')[-1]
			list[type][title][model][name] = {'type': 'file', 'path': item['paths'][0]}

def traverse(name, node):
	# os.chdir(rootdir)
	if node['type'] == 'folder':
		newdir = os.path.join(os.curdir, name)
		try:
			os.stat(newdir)
		except FileNotFoundError:
			os.mkdir(newdir)
		os.chdir(newdir)
		for (child_name, child) in node.items():
			if child_name == 'type': continue
			traverse(child_name, child)
		os.chdir(os.path.pardir)
	elif node['type'] == 'file':
		shutil.copy(os.path.join(rootdir, node['path']), name)
	else:
		raise TypeError(f"Invalid node type '{node['type']}'")

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: sort.py <index>")
		sys.exit()

	sort(sys.argv[1])

	rootdir = os.path.abspath(os.curdir)
	outdir = os.path.join(os.path.abspath(os.curdir), 'sorted')

	try:
		os.stat(outdir)
	except FileNotFoundError:
		os.mkdir(outdir)
	os.chdir(outdir)

	for (name, node) in list.items():
		traverse(name, node)