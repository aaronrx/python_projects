import os, glob, re, sys, datetime
from PyPDF2 import PdfFileMerger, PdfFileReader
from pathlib import Path
from shutil import rmtree
from zipfile import ZipFile


def create_directories():
    """Create required directories if they don't exist"""
    # try:
    directories = ('Actual_Results', 'Expected_Results', 'output', 'archive')
    dir_paths = [os.path.join(os.getcwd(), directory) for directory in directories]

    try:
        for dir_path in dir_paths:
            if os.path.exists(dir_path) and os.path.isfile(dir_path):
                # Raise exception if a file exists in the supposed path of the directory.
                raise FileExistsError('Unable to create required directory. File exists in "{}".'.format(dir_path))
            elif not os.path.exists(dir_path):
                os.mkdir(dir_path)

    except FileExistsError as e:
        abort_program(e)


def get_pdf_list(directory):
    """List and sort all available letters in Actual and Expected directories
       and then return the details as a dictionary.
    """

    # List all pdf files inside path
    pdfFiles = glob.glob("./{}/*.pdf".format(directory))

    # Regex patterns...
    refnoPattern = "[A-Z0-9]{1,2}[0-9]{5}"
    letterIDPattern = "{}.(.*?)_{}".format(directory, refnoPattern)

    # Extract letterIDs from pdfFiles list
    letterIDList = set(re.findall(letterIDPattern, "".join(pdfFiles)))

    return {letterID: [os.path.join(os.getcwd(), path)
                       for path in glob.glob("{}/*{}*.pdf".format(directory, letterID))] for letterID in letterIDList}


def get_master_list():
    """Get the common pdf files from the Actual and Expected file list."""
    actualResultsPDFList = get_pdf_list("Actual_Results")
    expectedResultsPDFList = get_pdf_list("Expected_Results")
    missingFiles = []

    masterList = {
        'Actual': dict(),
        'Expected': dict()
    }

    if actualResultsPDFList and expectedResultsPDFList:
        # Get common letterIDs
        letterIDs = set(actualResultsPDFList.keys()) & set(expectedResultsPDFList.keys())

        # Append files to missingFiles if their LetterIDs does not exist in both directories
        missingLetterIDs = [filename + "*.pdf"
                            for filename in set(actualResultsPDFList.keys()) ^ set(expectedResultsPDFList.keys())]
        missingFiles.extend(missingLetterIDs)

        refnoPattern = re.compile("[A-Z0-9]{1,2}[0-9]{5}")

        # Loop through the letterIDs
        for letterID in letterIDs:
            actualFilesList = actualResultsPDFList[letterID]
            expectedFilesList = expectedResultsPDFList[letterID]

            # List all refnos from both Actual and Expected directories
            actualRefnos = set(re.findall(refnoPattern, "".join(actualFilesList)))
            expectedRefnos = set(re.findall(refnoPattern, "".join(expectedFilesList)))

            # Get intersection of refnos....
            refnoList = actualRefnos & expectedRefnos

            def _get_files(fileListRaw):
                """Filters out files whose refno does not exist in either Actual or Expected and returns a sorted fileList"""
                fileList = []

                # Sort fileListRaw before the loop
                for file in sorted(fileListRaw):
                    # search for refno from the file path
                    match = re.search(refnoPattern, file)
                    if match and match.group() in refnoList:
                        fileList.append(os.path.join(os.getcwd(), file))
                    else:
                        # Append the missing file to the missingFiles list
                        source = Path(file).parts[-2]
                        if 'actual' in source.lower():
                            missingFiles.append(os.path.join(os.getcwd(), 'Expected_Results', file))
                        else:
                            missingFiles.append(os.path.join(os.getcwd(), 'Actual_Results', file))

                return fileList

            masterList['Actual'][letterID] = _get_files(actualFilesList)
            masterList['Expected'][letterID] = _get_files(expectedFilesList)

        # Info: Missing files
        if missingFiles:
            print('Missing Files:')
            for missingFile in missingFiles:
                print('  {}'.format(missingFile))
            else:
                print()

    return masterList


def merge_files(fileList):
    """Merge the files from fileList."""

    # TODO: Abort program if lists are not aligned/sorted properly... use Path.sort()?
    # Create a tmp directory
    try:
        pid = os.getpid()
        tmpDir = os.path.join(os.getcwd(), 'tmp{}'.format(pid))
        if not os.path.exists(tmpDir):
            os.mkdir(tmpDir)

    except Exception as e:
        errMsg = 'Unable to create tmp{} directory.'.format(pid)
        abort_program(errMsg, e)

    pdfFileMergerActual = PdfFileMerger()
    pdfFileMergerExpected = PdfFileMerger()
    blankPDF = os.path.join(os.getcwd(), 'PyPDF2/blankPDF.pdf')

    letterIDs = fileList['Expected'].keys()

    for letterID in letterIDs:
        actualLetters = fileList['Actual'][letterID]
        expectedLetters = fileList['Expected'][letterID]

        filesMerged = 0
        for actualLetter, expectedLetter in zip(actualLetters, expectedLetters):

            # Get the page count of both files
            with open(actualLetter, 'rb') as fileObj:
                actualLetterPageCount = PdfFileReader(fileObj).getNumPages()

            with open(expectedLetter, 'rb') as fileObj:
                expectedLetterPageCount = PdfFileReader(fileObj).getNumPages()

            # Check if pageCount does not match
            if actualLetterPageCount != expectedLetterPageCount:
                # Add blankpage and save as a tmpfile
                pdfFileBlankMerger = PdfFileMerger()
                blankPagesToAdd = abs(actualLetterPageCount - expectedLetterPageCount)
                tmpFile = expectedLetter.replace('Expected_Results', '{}'.format(Path(tmpDir).parts[-1]))
                actualGtExpected = False

                if actualLetterPageCount > expectedLetterPageCount:
                    pdfFileBlankMerger.append(expectedLetter)
                    pdfFileMergerActual.append(actualLetter)
                    actualGtExpected = True
                    print('Adding {} blank page(s) to {}.'.format(blankPagesToAdd, expectedLetter))

                elif actualLetterPageCount < expectedLetterPageCount:
                    pdfFileBlankMerger.append(actualLetter)
                    pdfFileMergerExpected.append(expectedLetter)
                    print('Adding {} blank page(s) to {}.'.format(blankPagesToAdd, actualLetter))

                while blankPagesToAdd > 0:
                    pdfFileBlankMerger.append(blankPDF)
                    blankPagesToAdd -= 1

                with open(tmpFile, 'wb') as fileObj:
                    pdfFileBlankMerger.write(fileObj)

                if actualGtExpected:
                    pdfFileMergerExpected.append(tmpFile)
                else:
                    pdfFileMergerActual.append(tmpFile)

            else:
                pdfFileMergerActual.append(actualLetter)
                pdfFileMergerExpected.append(expectedLetter)

            filesMerged += 1

        outFileActual = os.path.join(os.getcwd(), 'output/merged_Actual_{}.pdf'.format(letterID))
        outFileExpected = os.path.join(os.getcwd(), 'output/merged_Expected_{}.pdf'.format(letterID))

        try:
            # Save the merged pdf files
            with open(outFileActual, 'wb') as fileObj:
                pdfFileMergerActual.write(fileObj)

            with open(outFileExpected, 'wb') as fileObj:
                pdfFileMergerExpected.write(fileObj)

            print('Files merged for {}: {}'.format(letterID, filesMerged))

            # Reset the PdfFileMerger objects
            pdfFileMergerActual = PdfFileMerger()
            pdfFileMergerExpected = PdfFileMerger()

        except IsADirectoryError:
            abort_program("Unable to save {} file due to an existing directory with the same name.".format(fileObj.name))
        except PermissionError:
            abort_program("Unable to save {} file due to permission issues.".format(fileObj.name))

    # Clean-up created temporary files.
    clean_up()

    # Archive successfully processed files
    # archive_files(filePaths, letterID)


def clean_up():
    """Delete temporary files and directories created in the merging process."""
    try:
        tmpDirs = glob.glob('tmp*')

        # Skip deleting tmpdir of the current process.
        # tmpDirs.remove('tmp{}'.format(os.getpid()))

        # Delete tmp directories.
        [rmtree(os.path.join(os.getcwd(), tmpDir)) for tmpDir in tmpDirs]

    except NotADirectoryError as e:
        abort_program(e)
    except PermissionError as e:
        abort_program("Unable to delete tmp directory due to permission issues.", e)


def archive_files(filePaths, letterID):
    """Archive input files."""

    try:
        directory = Path(filePaths[0]).parts[0]
        timestamp = str(datetime.datetime.now().date())
        zip_file = "./archive/{}_{}_{}.zip".format(directory, letterID, timestamp)

        # compress files into a zipfile
        with ZipFile(zip_file, 'w') as fh:
            # write each file one by one
            [fh.write(file) for file in filePaths]

        # delete the files now that we have saved them.
        [os.remove(file) for file in filePaths]
    except IsADirectoryError as e:
        abort_program(e)


def abort_program(err_msg, exception_msg=None):
    """Display error  and abort the program."""
    print("Abort: {}".format(err_msg))
    if exception_msg:
        print("Error: {}".format(exception_msg))
    sys.exit(1)


def create_logs():
    """Create log files."""
    pass
    # TODO: Finish create_log()
