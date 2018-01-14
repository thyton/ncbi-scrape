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
geneData = {}
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
		    
			geneData['Phenotype Description'] = [phenoDesc] if bool(phenoDesc.strip()) else []
			geneData['Gene Name'] = geneName			
			geneData['HGNC ID'] = hgnc
			geneData['Gene Stable ID'] = geneStableID
			geneData['Found in NCBI'] = False
			countFile.write(entrezGeneID)

			# web scrape
			r = requests.get("https://www.ncbi.nlm.nih.gov/gene/" + entrezGeneID)
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
						 		geneData[key] = c.text.split('; ')	
						 		geneData['Found in NCBI'] = geneData['Gene Name'] in geneData[key] 
						   
					 		elif key == 'See related' or key == 'Orthologs':
					 			geneData[key] = {}
					 			for child in c.children:
					 				try:
					 					k = str(child.contents[0].strip(';'))
					 					geneData[key][k] = child['href']
					 				except AttributeError:
					 					continue
			 				else:
			 					info = c.contents[0]
			 					if info == '\n':
			 						geneData[key] = c.contents[1].text	
			 					else:
			 						geneData[key] = info
					try:
						if not geneData['Found in NCBI']:
							geneData['Found in NCBI']  = geneData['Gene Name'] == geneData['Official Symbol'] 
					except KeyError:
						errorFile.write(entrezGeneID + " no Official Symbol")

				except AttributeError:
					errorFile.write(entrezGeneID)
					errorFile.write(summary.prettify())

			print('"' + entrezGeneID + '":')
			print(json.dumps(geneData, sort_keys=False, indent=4))

			geneData = {}

		# update col
		col += 1
			
	except EOFError:
		break

		
errorFile.close()
countFile.close()







