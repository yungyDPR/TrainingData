## Features

Each TEI file has its raw file. A raw file is used by GROBID during training and stores features information. 

For the high level segmentation, the features are the following :

* Token
* Second token
* Lowercase first token
* Prefix 1-4 characters
* Block info
* page info
* Font info
* Bold info
* Italic info
* Capitalization
* Digits
* Character
* Dict info 
* relative document position
* relative page position coordinate
* punctuation profile
* number of punctuation characters in the line
* (scaled) line length
* bitmap connected to the current block
* vector graphic connected to the current block
* pattern repeated on several pages
* if we have a repeated pattern, indicate the first
* if the block is in the page main area

Source documents were parsed by lines.
