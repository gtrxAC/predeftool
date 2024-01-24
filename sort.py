# ______________________________________________________________________________
#
#  Sort content (apps, games, themes) into another folder based on metadata
#  in the JSON index file
# ______________________________________________________________________________
#
import os, sys, re
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
				type = re.sub(r"Nokia.*?$", "", item['Nokia-MIDlet-Category']) + 's'
			else:
				type = 'Applications'
		elif 'MIDlet-1' not in item:
			if item['type'] == 'theme':
				type = 'Themes'
			elif item['type'] == 'swf':
				type = 'Flash Lite'
			else:
				type = 'Unknown'
		else:
			type = 'Third-party'

		# Some third-party apps have Nokia as the vendor but the info URL field is one way to spot them
		if 'MIDlet-Info-URL' in item:
			type = 'Third-party'

		if type not in list: list[type] = {'type': 'folder'}

		# /Applications/Snake EX2
		if 'MIDlet-Name' in item:
			title = item['MIDlet-Name']
		else:
			# For non-java content, simply remove the file extension of the file path
			title = re.sub(r"\.\w+$", "", item['paths'][0].split('/')[-1])
		if title not in list[type]: list[type][title] = {'type': 'folder'}

		# /Applications/Snake EX2/128x160_6070/
		modeltype = re.search(r"content/([a-zA-Z]+[_-]?[\da-zA-Z]*?)(_|dp)", item['paths'][0]).group(1).replace('-', '').replace('_', '').lower()
		if modeltype in resolutions:
			model = resolutions[modeltype]
		else:
			raise KeyError(f"'{modeltype}' is not in resolutions.json")
		if model not in list[type][title]: list[type][title][model] = {'type': 'folder'}

		# Use a version subfolder for jars, no version for themes or SWFs
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
			# list[type][title][model]['rename_dupes'] = True
			if name not in list[type][title][model]:
				list[type][title][model][name] = {'type': 'filelist', 'paths': []}

			list[type][title][model][name]['paths'].append(item['paths'][0])

def traverse(name, node):
	if 'path' in node: node['path'] = node['path'].replace('\\x', '')
	name = name.replace('\\x', '')

	if node['type'] == 'folder':
		# if name in list[type][title][model]:
		# 	name = item['paths'][0].split('/')[2].split('.image_')[1] + '_' + name

		newdir = os.path.join(os.curdir, re.sub(r'[\\/:\*\?"<>\|\u0000]', '', name))
		try:
			os.stat(newdir)
		except FileNotFoundError:
			os.mkdir(newdir)
		os.chdir(newdir)

		for (child_name, child) in node.items():
			if child_name in ['type', 'rename_dupes']: continue
			traverse(child_name, child)
		os.chdir(os.path.pardir)
	elif node['type'] == 'file':
		shutil.copy(os.path.join(rootdir, node['path']), name)
		if node['path'].endswith('.jar'):
			try:
				shutil.copy(os.path.join(rootdir, node['path']).replace('.jar', '.jad'), name.replace('.jar', '.jad'))
			except:
				pass
	elif node['type'] == 'filelist':
		for path in node['paths']:
			if len(node['paths']) > 1:
				destname = path.split('/')[2].split('.image_')[1] + '_' + name
			else:
				destname = name

			try:
				shutil.copy(os.path.join(rootdir, path), destname)
			except:
				pass
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