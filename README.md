# Entrez-Gene-Summary-scraper
Obtaining entrez gene summaries from NCBI's eutils API

This tool will parse entrez gene IDs from a csv file and query them through NCBI's eutils API to obtain the Entrez summary for each gene when available.
It will then map each Entrez Summary to each Entrez ID within the csv of genes, and return an exported excel file with a new column of Entrez summaries.
