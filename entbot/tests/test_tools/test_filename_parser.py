import os
import sys
from entbot.tools.filename_parser import (
    get_cm_folder_path,
    get_filename_nb,
    get_file_extension,
    get_nb_origin_same_filename,
    get_school_year,
    get_valid_filename,
    turn_cwd_to_execution_dir,
)


def test_get_valid_filename():
    assert get_valid_filename("???^^@#test//\\.pdf") == "test"
    assert get_valid_filename("???^^@#test//\\") == "test"


def test_get_nb_origin_same_filename():
    test_filename = get_valid_filename(__file__.split("/")[-1])
    nb_same_filename = get_nb_origin_same_filename(
        folder_path=os.path.dirname(__file__), filename=test_filename
    )
    assert nb_same_filename == 1


def test_get_filename_nb():
    test_filename = get_valid_filename(__file__.split("/")[-1])
    filename_nb = get_filename_nb(
        folder_path=os.path.dirname(__file__), filename=test_filename
    )
    assert filename_nb == f"{test_filename}_1"


def test_get_file_extension():
    test_extension = get_file_extension(
        "https://test/resource/image.jpg", "Image/jpeg", "resource"
    )
    assert test_extension == ".jpg"
    test_extension = get_file_extension(
        "https://test/resource/image.jpg", "text/html", "resource"
    )
    assert test_extension == ".jpg"
    test_extension = get_file_extension(
        "https://test/resource/image", "Image/jpeg", "resource"
    )
    assert test_extension == ".jpg"
    test_extension = get_file_extension(
        "https://test/resource/image", "text/html", "resource"
    )
    assert test_extension == ""
    test_extension = get_file_extension(
        "https://test/resource/image", "text/html", "folder"
    )
    assert test_extension == ".zip"
    test_extension = get_file_extension(
        "https://test/resource/image", "text/html", "quiz"
    )
    assert test_extension == ""


def test_turn_cwd_to_execution_dir():
    turn_cwd_to_execution_dir()
    execution_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    assert os.getcwd() == execution_dir


def test_get_school_year():
    assert (
        get_school_year(
            "[23-24]test_course_name", start_date_timestamp=1693519200
        )
        == "23-24"
    )
    assert (
        get_school_year("test_course_name", start_date_timestamp=1693519200)
        == "23-24"
    )


def test_get_cm_folder_path():
    test_folder_path = get_cm_folder_path(
        "23-24", "[23-24] test_course_name", "test_topic_name"
    )
    assert (
        test_folder_path
        == "Fichiers_Ametice/23-24/23-24_test_course_name/test_topic_name"
    )
