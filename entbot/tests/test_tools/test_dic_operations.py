from entbot.tools.dic_operations import get_classified_cm_id


def test_get_classified_cm_id():
    table_topics_example = [
        {
            "id": "1012695",
            "section": 1,
            "number": 1,
            "title": "Chapitre 1: Groupes",
            "hassummary": False,
            "rawtitle": "Chapitre 1: Groupes",
            "cmlist": ["3282182", "3282183"],
            "visible": True,
            "sectionurl": "https://ametice.univ-amu.fr/course/view.php?id=113761#section-1",
            "current": False,
            "indexcollapsed": False,
            "contentcollapsed": False,
            "hasrestrictions": False,
        },
    ]
    print(type(table_topics_example))

    dic = get_classified_cm_id(table_topics_example)
    assert dic == {
        "3282182": "Chapitre 1: Groupes",
        "3282183": "Chapitre 1: Groupes",
    }
