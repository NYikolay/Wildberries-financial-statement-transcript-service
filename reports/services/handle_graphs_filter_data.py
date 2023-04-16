from typing import List


def get_filter_data(filter_dict: dict) -> List[dict]:
    valid_filter_list: List[dict] = []
    current_filters_names = set()

    for dict_values in filter_dict:
        new_filter_dict: dict = dict()
        new_filter_dict['year'] = int(dict_values)
        new_filter_dict['week_nums'] = list(map(int, filter_dict[dict_values][0].split(',')))
        current_filters_names.add('year')
        current_filters_names.add('week_nums')
        valid_filter_list.append(new_filter_dict)

    return valid_filter_list
