from re import finditer, compile
from typing import List
import inflect
inflect_engine = inflect.engine()  # used for same word comparing
import os
import boto3

_camel_case_regex_compiled = compile(
    r".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)")

def _create_boto_session():
    profile_name = os.environ.get('AWS_PROFILE', False)
    region_name = os.environ.get('AWS_REGION', False)
    _kwargs_dict = {}
    if profile_name:
        _kwargs_dict['profile_name']=profile_name
    if region_name:
        _kwargs_dict['region_name']=region_name
    session = boto3.session.Session(**_kwargs_dict)
    return session 

def ifind_similar_names_in_list(search_for, search_in_list):
    # TODO: regex support
    result = [] 
    if not search_for:
        return result
    lower_search_for = search_for.lower()
    
    for l_name in search_in_list:
        if l_name.lower().startswith(lower_search_for):
            result.append(l_name)
    return result
# >>> items = set([-1, 0, 1, 2])
# >>> set([1, 2]).issubset(items)
# True
# >>> set([1, 3]).issubset(items)
# False

def str_relations(relations):
    return ", ".join([
        f"[{r.get('service_name')}.{r.get('operation_name')} > {r.get('target_path')}]"
        for r in relations
    ])

def get_all_available_services(session) -> List[str]:
    return session.get_available_services()

def compare_nouns(word1: str, word2: str):
    return inflect_engine.compare_nouns(word1, word2)

def compare_two_token_lists(token_list_one, token_list_two):
    if len(token_list_one) != len(token_list_two):
        return False
    token_by_token_match = [
        w1.lower()==w2.lower()
        for w1, w2 in zip(token_list_one, token_list_two)
    ]
    has_token_by_token_match = all(token_by_token_match)
    return has_token_by_token_match

def icompare_two_token_lists(token_list_one, token_list_two):
    if len(token_list_one) != len(token_list_two):
        return False
    token_by_token_match = [
        bool(inflect_engine.compare_nouns(w1.lower(), w2.lower()))
        for w1, w2 in zip(token_list_one, token_list_two)
    ]
    has_token_by_token_match = all(token_by_token_match)
    return has_token_by_token_match

def camel_case_split(identifier: str) -> List[str]:
    """Splits camel case string to it's tokens"""
    matches = finditer(
        _camel_case_regex_compiled, identifier
    )
    return [m.group(0) for m in matches]

def compare_two_camel_case_words(word1, word2):
    token_list_1 = [_.lower() for _ in camel_case_split(word1)]
    token_list_2 = [_.lower() for _ in camel_case_split(word2)]
    return compare_two_token_lists(token_list_1, token_list_2)


def icompare_two_camel_case_words(word1, word2):
    token_list_1 = [_.lower() for _ in camel_case_split(word1)]
    token_list_2 = [_.lower() for _ in camel_case_split(word2)]
    return icompare_two_token_lists(token_list_1, token_list_2)

def compare_two_tokens(token_one, token_two):
    return bool(inflect_engine.compare_nouns(token_one, token_two))


def get_last_token_of_target_path(target_path, delimiter='.'):
    split_return_key = target_path.split(delimiter)
    *prev_return_keys, last_return_key_name = split_return_key
    return last_return_key_name