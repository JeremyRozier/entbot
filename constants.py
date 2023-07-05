import re

URL_LOGIN = "https://ident.univ-amu.fr/cas/login"
URL_AMETICE = "https://ident.univ-amu.fr/cas/login?service=https://ametice.univ-amu.fr/login/index.php?authCAS=CAS"

LIST_TYPES = ["assign", "folder", "resource", "url", "quiz", "choice", "forum"]
LIST_TREATED_TYPES = ["folder", "resource", "url"]
DIC_NAME_REGEX = {
    type_regex: re.compile(
        rf"https://ametice\.univ-amu\.fr/mod/{type_regex}/view\.php\?id=[0-9]+"
    )
    for type_regex in LIST_TREATED_TYPES
}
