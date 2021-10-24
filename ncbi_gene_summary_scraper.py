import urllib
import pandas as pd
from urllib.request import urlopen
import json
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

gene_ids_list_string_small = gene_ids_list_string[0:300]  # For testing


concatenated_list_Gene_IDs = []
nested_list_Gene_IDs = []


def get_chunks_in_list(input_list, chunk_size):
    """
    Returns generator object get_chunks_in_list
    For slicing list of Gene IDs into nested lists of chunk_size
    """
    return (input_list[pos:pos + chunk_size] for pos in range(0, len(input_list), chunk_size))


"""

"""
for chunks in get_chunks_in_list(gene_ids_list_string_small, 100):
    concatenated_list = ','.join(chunks)
    nested_list_Gene_IDs.append(chunks)
    concatenated_list_Gene_IDs.append(concatenated_list)


def generate_url_list(gene_id):
    """ This simple function takes in gene IDs and concatenates them into the url format that NCBI eutils expects. """
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=' \
          + gene_id \
          + '&retmode=json'
    return url


""" Enumerates through gene_ids_list_string to call generate_url_list and append generated urls to url_list """
url_list = []
for idx, concat_gene_list in enumerate(concatenated_list_Gene_IDs):
    url_list.append(generate_url_list(concat_gene_list))


def retrieve_ncbi_summary(url, list_of_gene_ids):
    """
    This functions takes in url as an argument and obtains the gene_id within the url.
    It then formats the origin of the request with a dummy browser, i.e. Mozilla.
    It loads the returned data as a json format and indexes the summary with data['result'][gene_id]['summary'].
    If there isn't any summary for that particular Entrez ID, it returns "No gene summary in NCBI".
    Else, it returns the summary as a string of text.
    """
    gene_ids_and_summaries = []
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(request)
    data = json.load(response)

    for gene_id in list_of_gene_ids:
        summary = data['result'][gene_id]['summary']
        if len(summary) == 0 or summary is None:
            summary_result = (gene_id, "No gene summary in NCBI")
        else:
            summary_result = (gene_id, summary)
        gene_ids_and_summaries.append(summary_result)

    return gene_ids_and_summaries


results = []

for ncbi_url, ncbi_list_of_gene_ids in zip(url_list, nested_list_Gene_IDs):
    returned_summaries = retrieve_ncbi_summary(ncbi_url, ncbi_list_of_gene_ids)
    results.extend(returned_summaries)


print(datetime.now() - startTime)
