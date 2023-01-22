import regex as re

list_types_regex = [
    "assign",
    "assignment",
    "folder",
    "resource",
    "url",
    "quiz",
    "choice",
    "data",
    "forum",
    "zoom",
    "chat",
    "book",
    "glossary",
    "bigbluebuttonbn",
    "feedback",
    "h5pactivity",
    "imscp",
    "lesson",
    "lti",
    "scorm",
    "survey",
    "wiki",
    "workshop",
]
DIC_NAME_REGEX = {
    type_regex: re.compile(
        rf"https://ametice\.univ-amu\.fr/mod/{type_regex}/view\.php\?id=[0-9]+"
    )
    for type_regex in list_types_regex
}
LIST_TREATED_TYPES = ["folder", "resource", "url"]
