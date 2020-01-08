#!/usr/bin/python3

#######################################################################################
#
# Program name  : pdf_merger.py
# Description   : Sort and merge the actual and expected PDF results into two separate PDFs.
#                 Works with multiple LetterIDs.
#
# Usage         : Put the PDF files in Actual_Results and Expected_Results directories
#                 then run pdf_merger.py.
#
#######################################################################################

from functions import *

print('Running pdf_merger.py...')
create_directories()
masterList = get_master_list()
merge_files(masterList)
print('Done.')
