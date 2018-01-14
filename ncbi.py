#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
from bs4 import BeautifulSoup
import string
import re
import requests
import json
from sys import stdin

"""
   The file ncbi_genes_formatted.txt contains gene data:
      1. gene stable id
      2. gene name
      3. phenotype description
      4. hgnc id
      5. entrezGene id
   These data of each gene are placed in 5 lines in that order. 
   Each data, unless specified, is of value 'EMPTY'

"""
errorFile = open("ncbi-errors",'w')
countFile = open("count","w")
col = 1
geneStableID = ""
geneName = "" 
phenoDesc = ""
hgnc = ""
entrezGeneID = ""
genes = {}
# extract the newline character
while True:
	try:
		info = input()
		if col == 1:
			geneStableID = info		
		elif col == 2 : 
			geneName = info
		elif col == 3:
			phenoDesc = info
		elif col == 4:
			hgnc = info
		else :
			entrezGeneID = info	
			col = 0
		
			genes[entrezGeneID] = {} if phenoDesc == '' else {phenoDesc}
			genes[entrezGeneID]['Phenotype Description'] = [phenoDesc] if bool(phenoDesc.strip()) else []
			genes[entrezGeneID]['Gene Name'] = geneName			
			genes[entrezGeneID]['HGNC ID'] = hgnc
			genes[entrezGeneID]['Gene Stable ID'] = geneStableID
			genes[entrezGeneID]['Found in NCBI'] = False
			countFile.write(entrezGeneID)
		# update col
		col += 1
			
	except EOFError:
		break

# scrape web
for g in genes.keys():
	r = requests.get("https://www.ncbi.nlm.nih.gov/gene/" + g)
	soup = BeautifulSoup(r.content, "lxml")

	# validates the geneStableID
	title =  soup.find("title");
	noItemFound = re.compile("No items found")

	if noItemFound.search(title.text) is None:
		
		summary = soup.find('dl', {"id":'summaryDl'})
		key = ''
		officialSymbol = re.compile("Official\s+Symbol")
		officialFullName = re.compile("Official\s+Full\s+Name")
		
		try:
			for c in summary.children:
				if c.name == 'dt':
					if(officialSymbol.search(c.text) is not None):
						key = 'Official Symbol'
					elif(officialFullName.search(c.text) is not None):
						key = 'Official Full Name'
					else:
						key = c.text

				elif c.name == 'dd':
				 	if key == 'Also known as':
				 		genes[g][key] = c.text.split('; ')	
				 		genes[g]['Found in NCBI'] = genes[g]['Gene Name'] in genes[g][key] 
				   
			 		elif key == 'See related' or key == 'Orthologs':
			 			genes[g][key] = {}
			 			for child in c.children:
			 				try:
			 					k = str(child.contents[0].strip(';'))
			 					genes[g][key][k] = child['href']
			 				except AttributeError:
			 					continue
	 				else:
	 					info = c.contents[0]
	 					if info == '\n':
	 						genes[g][key] = c.contents[1].text	
	 					else:
	 						genes[g][key] = info
			try:
				if not genes[g]['Found in NCBI']:
					genes[g]['Found in NCBI']  = genes[g]['Gene Name'] == genes[g]['Official Symbol'] 
			except KeyError:
				continue

		except AttributeError:
			errorFile.write(g)
			errorFile.write(summary.prettify())
			continue		

	print('"' + str(g) + '":')
	print(json.dumps(genes[g], sort_keys=False, indent=4))
		
errorFile.close()
countFile.close()







