import os

from bs4 import BeautifulSoup
import PyPDF2
import requests


def get_pdf_from_bnf_api_sru(query_parameter: str, download_dir: str):
    ark_ids = {}
    if " " in query_parameter:
        query_parameter = query_parameter.replace(" ", "%20")

    query_url = f"https://catalogue.bnf.fr/api/SRU?version=1.2&operation=searchRetrieve&query=bib.anywhere%20all%20%22{query_parameter}%22and%20bib.digitized%20all%20%22freeAccess%22&startRecord=1&maximumRecords=100"
    print(f"Fetching: {query_url}")

    if requests.get(query_url).status_code == 200:
        print("Request successfully fetched. Beginning parsing.\n")
        r = requests.get(query_url)
        r_content = r.content
    else:
        print(f"Query failed. HTTP status code : {requests.get(query_url).status_code}")
        return None

    parsed_content = BeautifulSoup(r_content, "lxml")
    records_number = parsed_content.find('srw:numberofrecords').string
    print(f"Number of records found : {records_number}\n")

    for record in parsed_content.find_all('mxc:record'):
        gallic_ark = [child.string for child in record.find_all('mxc:subfield') if child['code'] == 'u']
        ark_ids[record['id']] = gallic_ark

    print(f"Ark identifiers stored. Beginning PDF download query to Gallica API.")

    for item in ark_ids.items():
        if len(item[1]) < 2:
            url = ''.join(item[1])
            url_pdf = url + '.pdf'
            print(f'Downloading {url_pdf}...')
            file_name = '-'.join(url_pdf.split('/')[-2:])
            response = requests.get(url_pdf)
            with open(f'{download_dir}/{file_name}', 'wb+') as f:
                f.write(response.content)
        else:
            for ark in item[1]:
                url = ''.join(ark)
                url_pdf = url + '.pdf'
                print(f'Downloading {url_pdf}...')
                file_name = '-'.join(url_pdf.split('/')[-2:])
                response = requests.get(f'{url}.pdf')
                with open(f'{download_dir}/{file_name}', 'wb+') as f:
                    f.write(response.content)

    print(" \nDone.")


def preprocess_pdf(input_dir: str, output_dir: str, pages_to_delete: list):
    """
    Pre-process a PDF before processing with GROBID.
    Check if each PDF in a directory contains text
    and erase first two pages (Gallica warning non relevant to document)

    :param input_dir: path to directory where pdf are located
    :param output_dir: path to directory where pre-processed pdf will be generated
    :param pages_to_delete: pages that will be deleted
    :return: null
    """
    file_nb = 0
    processed_files = 0
    skipped_files = 0
    for file in os.listdir(input_dir):
        has_text = False
        if file.endswith('.pdf'):
            file_nb += 1
            try:
                with open(f'{input_dir}/{file}', 'rb') as pdf_file_obj:
                    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)

                    for i in range(pdf_reader.getNumPages()):
                        if i not in pages_to_delete:
                            if pdf_reader.getPage(i).extractText():
                                has_text = True

                    if has_text:
                        processed_files += 1
                        print(f"Text blocks were found. Processing \t {file.title()}")
                        output = PyPDF2.PdfFileWriter()
                        for i in range(pdf_reader.getNumPages()):
                            if i not in pages_to_delete:
                                p = pdf_reader.getPage(i)
                                output.addPage(p)
                        with open(f'{output_dir}/{file}', 'wb+') as f:
                            output.write(f)

                    elif has_text == False:
                        print(f"No text block was found. \t {file.title()} was not processed.")
                        skipped_files += 1

            except PyPDF2.utils.PdfReadError as e:
                print(f"Error on file {file} : {e}. Not processed.")

    print("\n")
    print(f"{processed_files} out of {file_nb} files were processed.")
    print(f"{skipped_files} out of {file_nb} files were skipped. See logs in output directory.")


preprocess_pdf('../raw_pdf', '../preprocessed_pdf', [0, 1])
# get_pdf_from_bnf_api_sru("ventemma naville", '../download_dir')
