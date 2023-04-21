from collections import Counter
from re import finditer, compile
from typing import List
import inflect
import os
import boto3
from config import get_logger

# from functools import lru_cache

inflect_engine = inflect.engine()  # used for singular/plural word comparing
logger = get_logger(__name__)

_camel_case_regex_compiled = compile(
    r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)"
)


def _create_boto_session():
    profile_name = os.environ.get("AWS_PROFILE", False)
    region_name = os.environ.get("AWS_REGION", False)
    _kwargs_dict = {}
    if profile_name:
        _kwargs_dict["profile_name"] = profile_name
    if region_name:
        _kwargs_dict["region_name"] = region_name
    session = boto3.session.Session(**_kwargs_dict)
    return session


def are_two_lists_same(list_one: List, list_two: List) -> bool:
    """Compares the contents of two lists"""
    return Counter(list_one) == Counter(list_two)


def is_word_in_a_list_of_words(word: str, list_of_words: List[str]) -> bool:
    """Checks if a word is a is in a list_of_words, case insensitive"""
    lower_word = word.lower()
    for a_word in list_of_words:
        if lower_word == a_word.lower():
            return True
    return False

    return word.lower() in []


def inform_about_develeoping_custom_resource_nodes():
    logger.debug(
        "[bold yellow][WARNING][/] It seems balcony [red bold]failed[/] to read this operation. You can create Custom ResourceNodes to fix the failed operation. Visit [bold]https://oguzhan-yilmaz.github.io/balcony/development/developing-custom-resource-nodes/[/] to learn more."
    )


def ifind_similar_names_in_list(
    search_for: str, search_in_list: List[str]
) -> List[str]:
    """Case insensitive find in list"""
    result = []
    if not search_for or not search_in_list:
        return result
    lower_search_for = search_for.lower()

    for l_name in search_in_list:
        if l_name.lower().startswith(lower_search_for):
            result.append(l_name)
    return result


def str_relations(relations: List[dict]) -> str:
    """Stringify list of relations"""
    return ", ".join(
        [f"[{r.service_name}.{r.operation_name} > {r.target_path}]" for r in relations]
    )


def get_all_available_services(session: boto3.session.Session) -> List[str]:
    """Gets available services from boto3 session"""
    return session.get_available_services()


def compare_nouns(word1: str, word2: str) -> bool:
    """Singular/plural insensitive word comparison"""
    return inflect_engine.compare_nouns(word1, word2)


def compare_two_token_lists(
    token_list_one: List[str], token_list_two: List[str]
) -> bool:
    """Compares to word lists one by one in lowercase"""
    if len(token_list_one) != len(token_list_two):
        return False
    token_by_token_match = [
        w1.lower() == w2.lower() for w1, w2 in zip(token_list_one, token_list_two)
    ]
    has_token_by_token_match = all(token_by_token_match)
    return has_token_by_token_match


def icompare_two_token_lists(
    token_list_one: List[str], token_list_two: List[str]
) -> bool:
    """Singular/plural insensitive token list comparison"""
    if len(token_list_one) != len(token_list_two):
        return False
    token_by_token_match = [
        bool(inflect_engine.compare_nouns(w1.lower(), w2.lower()))
        for w1, w2 in zip(token_list_one, token_list_two)
    ]
    has_token_by_token_match = all(token_by_token_match)
    return has_token_by_token_match


def camel_case_split(identifier: str) -> List[str]:
    """Splits CamelCase string to it's tokens"""
    matches = finditer(_camel_case_regex_compiled, identifier)
    return [m.group(0) for m in matches]


def compare_two_camel_case_words(word1: str, word2: str) -> bool:
    token_list_1 = [_.lower() for _ in camel_case_split(word1)]
    token_list_2 = [_.lower() for _ in camel_case_split(word2)]
    return compare_two_token_lists(token_list_1, token_list_2)


def icompare_two_camel_case_words(word1: str, word2: str) -> bool:
    token_list_1 = [_.lower() for _ in camel_case_split(word1)]
    token_list_2 = [_.lower() for _ in camel_case_split(word2)]
    return icompare_two_token_lists(token_list_1, token_list_2)
