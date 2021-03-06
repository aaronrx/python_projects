import os, re, sys, logging
from os.path import split, basename
from shutil import rmtree
from glob import glob
from packages.PyPDF2 import PdfFileMerger, PdfFileReader


def set_log_configs():
    """Set log configs"""
    logging.basicConfig(filename="pdf_merger.log", level=logging.INFO, format='%(message)s', filemode='w')


def create_directories():
    """Create required directories if they don't exist"""
    # Create tmp dir for the merging process.
    tmp_directory = os.path.join(os.getcwd(), "tmp{}".format(os.getpid()))
    directories = ("Actual_Results", "Expected_Results", "output", tmp_directory)
    dir_paths = [os.path.join(os.getcwd(), directory) for directory in directories]

    try:
        for dir_path in dir_paths:
            if os.path.exists(dir_path) and os.path.isfile(dir_path):
                # Raise exception if a file exists in the supposed path of the directory.
                raise FileExistsError("Unable to create directory '{}' due to an existing file with the same name.".format(dir_path))
            elif not os.path.exists(dir_path):
                os.mkdir(dir_path)
    except FileExistsError as e:
        abort_program(e)


def setup():
    """Create required directories and set log configs"""
    set_log_configs()
    create_directories()


def get_complete_pdf_list(directory):
    """List and sort all available letters in Actual and Expected directories
       and then return the details as a dictionary.
    """

    # List all pdf files inside path
    pdf_files = glob("./{}/*.pdf".format(directory))

    # Regex patterns...
    refno_pattern = "[A-Z0-9]{1,2}[0-9]{5}"
    letter_id_pattern = "{}.(.*?)_{}".format(directory, refno_pattern)

    # Extract letterIDs from pdfFiles list
    letter_id_list = set(re.findall(letter_id_pattern, "".join(pdf_files)))

    # TODO: Find a better alternative for glob.
    return {letter_id: [os.path.join(os.getcwd(), path)
                        for path in glob("{}/*{}*.pdf".format(directory, letter_id))] for letter_id in letter_id_list}


def get_filtered_list(refno_pattern, common_refno_list, raw_file_list, missing_files):
    """Filters out files whose refno does not exist in either Actual or Expected and returns a sorted fileList"""
    file_list = []

    # Sort raw_file_list before the loop
    for file in sorted(raw_file_list):
        # search for refno from the file path
        match = re.search(refno_pattern, file)
        if match and match.group() in common_refno_list:
            file_list.append(os.path.join(os.getcwd(), file))
        else:
            # Append the missing file to the missing_files list
            source = basename(split(file)[0])
            if "actual" in source.lower():
                missing_files.append(os.path.join(os.getcwd(), "Expected_Results", file))
            else:
                missing_files.append(os.path.join(os.getcwd(), "Actual_Results", file))

    return file_list


def get_master_list():
    """Get the common pdf files from the Actual and Expected file list."""
    actual_results_pdf_list = get_complete_pdf_list("Actual_Results")
    expected_results_pdf_list = get_complete_pdf_list("Expected_Results")
    missing_files = []

    master_list = {
        "Actual": dict(),
        "Expected": dict()
    }

    if actual_results_pdf_list and expected_results_pdf_list:
        # Get common letterIDs
        letter_ids = set(actual_results_pdf_list.keys()) & set(expected_results_pdf_list.keys())

        # Append files to missingFiles if their LetterIDs do not exist in both directories
        [missing_files.append(filename + "*.pdf")
         for filename in set(actual_results_pdf_list.keys()) ^ set(expected_results_pdf_list.keys())]

        refno_pattern = re.compile("[A-Z0-9]{1,2}[0-9]{5}")

        # Loop through the letterIDs
        for letter_id in letter_ids:
            actual_file_list = actual_results_pdf_list[letter_id]
            expected_file_list = expected_results_pdf_list[letter_id]

            # List all refnos from both Actual and Expected directories
            actual_refnos = set(re.findall(refno_pattern, "".join(actual_file_list)))
            expected_refnos = set(re.findall(refno_pattern, "".join(expected_file_list)))

            # Get common refno list by executing set's intersection.
            common_refno_list = actual_refnos & expected_refnos

            master_list["Actual"][letter_id] = get_filtered_list(refno_pattern, common_refno_list, actual_file_list, missing_files)
            master_list["Expected"][letter_id] = get_filtered_list(refno_pattern, common_refno_list, expected_file_list, missing_files)

        # Info: Missing files
        if missing_files:
            logging.info("Missing files:")
            [logging.info("  {}".format(file)) for file in missing_files]
            logging.info("")

    return master_list


def merge_files(master_list):
    """Merge the files based from the master_list."""
    # TODO: Abort program if lists are not aligned/sorted properly...

    tmp_directory = os.path.join(os.getcwd(), "tmp{}".format(os.getpid()))

    pdf_merger_actual = PdfFileMerger()
    pdf_merger_expected = PdfFileMerger()
    blank_pdf_file = os.path.join(os.getcwd(), "files/blankPDF.pdf")
    letter_ids = master_list["Expected"].keys()

    try:
        for letter_id in letter_ids:
            actual_letters = master_list["Actual"][letter_id]
            expected_letters = master_list["Expected"][letter_id]
            logging.info("Processing {} files...".format(letter_id))

            files_merged_count = 0
            for actual_letter, expected_letter in zip(actual_letters, expected_letters):
                # Get the page count of both files.
                with open(actual_letter, "rb") as fileObj:
                    actual_letter_page_count = PdfFileReader(fileObj).getNumPages()

                with open(expected_letter, "rb") as fileObj:
                    expected_letter_page_count = PdfFileReader(fileObj).getNumPages()

                # Check if pageCount does not match
                if actual_letter_page_count != expected_letter_page_count:
                    # Add a blank page and save as a tmp_file
                    pdf_merger_blank = PdfFileMerger()
                    num_of_blank_pages_to_add = abs(actual_letter_page_count - expected_letter_page_count)
                    tmp_file = expected_letter.replace("Expected_Results", "{}".format(basename(tmp_directory)))
                    actual_pg_count_gt_expected = actual_letter_page_count > expected_letter_page_count
                    if actual_pg_count_gt_expected:
                        pdf_merger_blank.append(expected_letter)
                        pdf_merger_actual.append(actual_letter)
                        logging.info("Added {} blank page(s) to {}.".format(num_of_blank_pages_to_add, expected_letter))
                    else:
                        pdf_merger_blank.append(actual_letter)
                        pdf_merger_expected.append(expected_letter)
                        logging.info("Added {} blank page(s) to {}.".format(num_of_blank_pages_to_add, actual_letter))

                    [pdf_merger_blank.append(blank_pdf_file) for _ in range(num_of_blank_pages_to_add)]

                    # Save modified pdf files as tmp files.
                    with open(tmp_file, "wb") as fileObj:
                        pdf_merger_blank.write(fileObj)

                    # Add the tmp_file to their respective merge list
                    if actual_pg_count_gt_expected:
                        pdf_merger_expected.append(tmp_file)
                    else:
                        pdf_merger_actual.append(tmp_file)
                else:
                    pdf_merger_actual.append(actual_letter)
                    pdf_merger_expected.append(expected_letter)

                files_merged_count += 1

            outfile_actual = os.path.join(os.getcwd(), "output/merged_Actual_{}.pdf".format(letter_id))
            outfile_expected = os.path.join(os.getcwd(), "output/merged_Expected_{}.pdf".format(letter_id))

            # Save the merged pdf files
            with open(outfile_actual, "wb") as fileObj:
                pdf_merger_actual.write(fileObj)

            with open(outfile_expected, "wb") as fileObj:
                pdf_merger_expected.write(fileObj)

            logging.info("")
            logging.info("Merged files: {}".format(files_merged_count))
            logging.info("Output:")
            logging.info("  " + outfile_actual)
            logging.info("  " + outfile_expected)

            # Reset the PdfFileMerger objects
            pdf_merger_actual = PdfFileMerger()
            pdf_merger_expected = PdfFileMerger()

    except IsADirectoryError:
        abort_program("Unable to save {} file due to an existing directory with the same name.".format(fileObj.name))
    except PermissionError:
        abort_program("Unable to save {} file due to permission issues.".format(fileObj.name))

    clean_up()


def clean_up():
    """Delete temporary files and directories created during the merging process."""
    try:
        tmp_directories = glob("tmp*")

        # TODO: Check PermissionError when program is ran on windows
        # Skip deleting tmp directory of the current process if os is not linux
        if sys.platform != "linux":
            tmp_directories.remove("tmp{}".format(os.getpid()))

        # Delete tmp directories.
        [rmtree(os.path.join(os.getcwd(), tmpDir)) for tmpDir in tmp_directories]

    except NotADirectoryError as e:
        abort_program(e)
    except PermissionError as e:
        abort_program("Unable to delete tmp directory due to permission issues.", e)


def abort_program(err_msg, exception_msg=None):
    """Display error and abort the program."""
    logging.error("{}".format(err_msg))
    if exception_msg:
        logging.error("Exception: {}".format(exception_msg))
    sys.exit(1)
