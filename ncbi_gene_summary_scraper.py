import urllib
import pandas as pd
from urllib.request import urlopen
import json
from datetime import datetime
import time
from termcolor import colored

# Internal modules
import gene_summary_dictionary

"""
ncbi_gene_summary_scraper.py
This script takes in a CSV file of genes with their Entrez IDs and parses these IDs via https request to get
Entrez summaries and other information from NCBI's eutils API, returned as JSON format.
"""


def get_chunks_in_list(input_list, chunk_size):
    """
    Returns generator object get_chunks_in_list
    For slicing list of Gene IDs into nested lists of chunk_size
    """
    return (input_list[pos:pos + chunk_size] for pos in range(0, len(input_list), chunk_size))


def generate_url_list(gene_id):
    """ This simple function takes in gene IDs and concatenates them into the url format that NCBI eutils expects. """
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=' \
          + gene_id \
          + '&retmode=json'
    return url


def retrieve_ncbi_summary(url, list_of_gene_ids, sleep):
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
    time.sleep(sleep)
    print("Data retrieved from url, delay for 3 seconds before parsing out summary.....")

    for gene_id in list_of_gene_ids:
        summary = data['result'][gene_id]['summary']
        if len(summary) == 0 or summary is None:
            summary_result = (gene_id, "No Entrez summary in NCBI")
        else:
            summary_result = (gene_id, summary)
        gene_ids_and_summaries.append(summary_result)

    return gene_ids_and_summaries


def main(gene_info_file, sleep_duration=3, chunk=300):
    """
    Main function
    Uses pandas to read CSV file containing list of genes, ideally with Entrez IDs
    Obtains unique Entrez IDs from the column "ENTREZID" with pd.unique
    Drops NAs and converts IDs from floats to integers
    Converts numpy array of IDs to list
    :param chunk:
    :param sleep_duration:
    :param gene_info_file:
    :return:
    """
    start_time = datetime.now()

    gene_info_file_csv = gene_info_file + ".csv"
    gene_data = pd.read_csv(gene_info_file_csv)
    gene_ids = pd.unique(gene_data["ENTREZID"].dropna().astype(int))
    gene_ids_list = gene_ids.tolist()
    # Using list comprehension
    gene_ids_list_string = [str(x) for x in gene_ids_list]

    print("Data imported and gene IDs converted to list.")

    concatenated_list_gene_ids = []
    nested_list_gene_ids = []

    """
    Based on the assigned chunk size, the list of Entrez IDs will be split into both nested list containing lists of
    Entrez IDs with length = chunk, and list of concatenated Entrez IDs, seperated only by "," to produce the url in the
    format that NCBI eutils expects
    """
    for chunks in get_chunks_in_list(gene_ids_list_string, chunk_size=chunk):
        gene_list_as_long_string = ','.join(chunks)
        nested_list_gene_ids.append(chunks)
        concatenated_list_gene_ids.append(gene_list_as_long_string)

    print("Chunks of gene IDs obtained.")

    """ Enumerates through gene_ids_list_string to call generate_url_list and append generated urls to url_list """
    url_list = []
    for idx, concat_gene_list in enumerate(concatenated_list_gene_ids):
        url_list.append(generate_url_list(concat_gene_list))

    print("Long urls of multiple Entrez IDs generated.")

    results = []

    """
    For each url of chunk number of genes, and corresponding nested list of gene IDs, the retrieve_ncbi_summary
    function is called once to get data, and list of tuples are stored as temporary variable: returned_summaries.
    Then returned_summaries is extended to results list as more tuples (gene_id, summary).
    """
    for ncbi_url, ncbi_list_of_gene_ids in zip(url_list, nested_list_gene_ids):
        returned_summaries = retrieve_ncbi_summary(ncbi_url, ncbi_list_of_gene_ids, sleep=sleep_duration)
        index = nested_list_gene_ids.index(ncbi_list_of_gene_ids)
        length_of_nested_list = len(nested_list_gene_ids)
        results.extend(returned_summaries)
        print(index + 1, "out of", length_of_nested_list, "chunks of Entrez IDs completed.")
        time_taken_1 = datetime.now() - start_time
        print(colored(f"Time taken = {time_taken_1}", "green"))

    print("Retrieved Entrez summaries from NCBI's eutils API.")

    """
    The list of tuples (gene_id, summary) are converted into a large dictionary with the generate_dictionary_from_tuple
    function. This dictionary is stored as dictionary_of_summaries.
    A new column of "ENTREZID_string" is created for subsequent mapping as dictionary keys are strings.
    For all rows without gene summaries, a default string is placed.
    String elements in column "ENTREZID_string" are mapped with dictionary_of_summaries to get the corresponding
    Entrez summaries, which replace the default string.
    Export to excel file with similar imported naming.
    """
    dictionary_of_summaries = gene_summary_dictionary.generate_dictionary_from_tuple(results)

    gene_data["ENTREZID_string"] = gene_data["ENTREZID"].dropna().astype(int).astype(str)
    gene_data["NCBI_ENTREZ_summaries"] = "Not a protein coding gene, no Entrez summary or no information available"
    gene_data["NCBI_ENTREZ_summaries"] = gene_data["ENTREZID_string"].map(dictionary_of_summaries) \
        .fillna(gene_data["NCBI_ENTREZ_summaries"])

    print("Mapped Entrez summaries to respective Entrez IDs as new column in dataframe.")

    gene_data_excel_export = gene_info_file + "_summary.xlsx"
    gene_data.to_excel(gene_data_excel_export)

    print("Exported excel file with original data and annotated Entrez summaries")
    time_taken_2 = datetime.now() - start_time
    print(colored(f"Time taken = {time_taken_2}", "green"))
