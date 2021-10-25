"""
For generation of dictionary with key as Entrez ID of gene and value as Entrez summary scraped from NCBI's eutils API
"""


def generate_dictionary_from_tuple(results_in_tuple):
    gene_summary_dict = dict(results_in_tuple)
    gene_summary_dict["default"] = "No gene summary available"
    return gene_summary_dict
