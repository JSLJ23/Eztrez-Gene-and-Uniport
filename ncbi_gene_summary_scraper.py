import urllib
import pandas as pd
from urllib.request import urlopen
import json
from multiprocessing.pool import ThreadPool
from datetime import datetime

"""
This script takes in a CSV file of genes with their Entrez IDs and parses these IDs via https request to get
Eztrez summaries and other information returned as JSON format. Only Entrez summaries are retained as that is
the main point of interest.

Uses pandas to read CSV file containing list of genes, ideally with Entrez IDs
Obtains unique Entrez IDs from the column 'ENTREZID' with pd.unique
Drops NAs and converts IDs from floats to intergers
Converts numpy array of IDs to list
"""

startTime = datetime.now()

gene_info_file = "Sox8_KD_sig_DEGs_with_description.csv"
gene_data = pd.read_csv(gene_info_file)
gene_ids = pd.unique(gene_data['ENTREZID'].dropna().astype(int))
gene_ids_list = gene_ids.tolist()
# Using list comprehension
gene_ids_list_string = [str(x) for x in gene_ids_list]


def get_chunks_in_list(input_list, chunk_size):
    """ Returns generator object get_chunks_in_list """
    return (input_list[pos:pos + chunk_size] for pos in range(0, len(input_list), chunk_size))


concatenated_list_Gene_IDs = []


"""

"""
for chunks in get_chunks_in_list(gene_ids_list_string, 100):
    concatenated_list = ','.join(chunks)
    concatenated_list_Gene_IDs.append(concatenated_list)


def generate_url_list(gene_id):
    """ This simple function takes in gene IDs and concatenates them into the url format that NCBI eutils expects. """
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=' \
          + gene_id \
          + '&retmode=json'
    return url


""" Enumerates through gene_ids_list_string to call generate_url_list and append generated urls to url_list """
url_list = []
for idx, gene in enumerate(gene_ids_list_string):
    url_list.append(generate_url_list(gene))


url_list_short = url_list[0:200]  # For small testing purposes, url list of first 100 elements


def retrieve_ncbi_summary(url):
    """
    This functions takes in url as an argument and obtains the gene_id within the url.
    It then formats the origin of the request with a dummy browser, i.e. Mozilla.
    It loads the returned data as a json format and indexes the summary with data['result'][gene_id]['summary'].
    If there isn't any summary for that particular Entrez ID, it returns "No gene summary in NCBI".
    Else, it returns the summary as a string of text.
    """
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = json.load(urllib.request.urlopen(req))
    start = url.find("gene&id=") + len("gene&id=")
    end = url.find("&retmode")
    gene_id = url[start:end]
    summary = data['result'][gene_id]['summary']
    if len(summary) == 0 or summary is None:
        return gene_id, "No gene summary in NCBI"
    else:
        return gene_id, summary


""" A list for the results is initialized for the multiprocessing results to be appended to"""
result_list = []

# Initialize a multiprocessing pool that will close after finishing execution.
results = ThreadPool(1).imap_unordered(retrieve_ncbi_summary, url_list_short)

for result in results:
    result_list.append(result)


print(datetime.now() - startTime)
