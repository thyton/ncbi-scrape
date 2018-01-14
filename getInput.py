#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
import json 

def getInput(fileName):
	col = 1
	geneStableID = ""
	geneName = "" 
	phenoDesc = ""
	hgnc = ""
	entrezGeneID = ""
	genes = {}
	with open(fileName) as inFile:
		# extract the newline character
		for line in inFile:
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

					if entrezGeneID in genes.keys() :
						genes[entrezGeneID].get('Phenotype Description').append(phenoDesc)

					else:
						genes[entrezGeneID] = {}
						genes[entrezGeneID]['Phenotype Description'] = [phenoDesc] if bool(phenoDesc.strip()) else []
						genes[entrezGeneID]['Gene Name'] = geneName			
						genes[entrezGeneID]['HGNC ID'] = hgnc
						genes[entrezGeneID]['Gene Stable ID'] = geneStableID
						genes[entrezGeneID]['Found in NCBI'] = False

				# update col
				col += 1
	return genes

if __name__ == '__main__':
	fileName = input()
	genes = getInput(fileName)
	print(len(genes))
	print(json.dumps(genes, sort_keys = False, indent = 2))
else:
	getInput(fileName)


