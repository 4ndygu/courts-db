from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from string import Template, punctuation
from glob import iglob
from io import open

import json
import six
import re
import os

db_root = os.path.dirname(os.path.realpath(__file__))


def get_court_data_from_ids(id_list):
    cd = {}
    for id in id_list:
        cd[id] = court
    return cd


def make_court_dictionary(courts):
    cd = {}
    for court in courts:
        cd[court["id"]] = court
    return cd


def load_courts_db():
    """Load the court data from disk, and render regex variables

    Court data is on disk as one main JSON file, another containing variables,
    and several others containing placenames. These get combined via Python's
    template system and loaded as a Python object

    :return: A python object containing the rendered courts DB
    """
    with open(os.path.join(db_root, "data", "variables.json"), "r") as v:
        variables = json.load(v)

    for path in iglob(os.path.join(db_root, "data", "places", "*.txt")):
        with open(path, "r") as p:
            places = "(%s)" % "|".join(p.read().splitlines())
            variables[path.split(os.path.sep)[-1].split(".txt")[0]] = places

    with open(os.path.join(db_root, "data", "courts.json"), "r") as f:
        s = Template(f.read()).substitute(**variables)
    s = s.replace("\\", "\\\\")

    return json.loads(s)


def gather_regexes(courts, bankruptcy=False, court_id=None):
    """Create a variable mapping regexes to court IDs

    :param courts: The court DB
    :type courts: list
    :param bankruptcy: Whether to include bankruptcy courts in the final
    mapping.
    :type bankruptcy: bool
    :return: A list of two-tuples, with tuple[0] being a compiled regex and
    tuple[1] being the court ID.
    :rtype: list
    """
    regexes = []
    for court in courts:
        if bankruptcy == False:
            if court["type"] == "bankruptcy":
                continue
        for reg_str in court["regex"]:
            regex = re.compile(reg_str, (re.I | re.U))
            regexes.append((regex, court["id"]))

    if court_id is not None:
        regexes = list(filter(lambda x: x[1] == court_id, regexes))

    return regexes
