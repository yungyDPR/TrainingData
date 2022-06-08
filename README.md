# Training datasets for training GROBID sale catalogues models

Each directory of this repository contains datasets created to train GROBID sale catalogues models. Datasets are divided based on where original documents are being kept, and then are organized by authors/auction houses.

Annotated files are in the [TEI-XML](https://tei-c.org/) format.

## Naming convention

* BnF files are named with their Gallica ark identifier.
* INHA files are named with their digital identifier ("identifiant numérique") provided in their online notice.

## GROBID models

* Segmentation : the segmentation model aims to obtain a high level segmentation of the catalogues. 

## Data quality

Before being pushed to the main branch, annotated files have at least been proofread once, and are validated with an XSD by a Github action.

# Toolbox

This repository also contains a set of tools that can be used on the training sets. 

* PDF Preprocessing
* Quality assessment
* XML validity checker (used by a Github action)

# DataCatalogue organization information

## Organization logo

Logo by [Alix Chagué](https://alix-tz.github.io/), inspiration from [Loading Artist](https://loadingartist.com/).
