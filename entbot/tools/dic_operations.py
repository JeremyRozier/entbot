"""Module that contains functions to make operations on dictionaries"""

def get_classified_cm_id(table_topics: list[dict]) -> dict[str, str]:
    """Creates a dictionary that maps the course module ids
    to the topic names associated.

    Args:
        - table_topics (list[dict]): The table containing
        all the data of the followed topics.

    Returns (dict): A dictionary that maps the course module ids
    to the topic names associated.
    """
    dic_cm_id_topic = {}
    for dic_topic in table_topics:
        topic_name = dic_topic["title"]
        list_cm_id = dic_topic["cmlist"]
        dic_cm_id_topic.update(
            dict(
                zip(
                    list_cm_id,
                    [topic_name for i in range(len(list_cm_id))],
                )
            )
        )
    return dic_cm_id_topic
