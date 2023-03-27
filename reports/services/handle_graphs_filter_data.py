from typing import List


def get_period_filter_data(filter_dict: dict) -> List[dict]:

    new_filter_list: List[dict] = []

    for dict_values in filter_dict:
        new_filter_dict: dict = dict()
        new_filter_dict['year'] = int(dict_values)
        new_filter_dict['week_nums'] = list(map(int, filter_dict[dict_values][0].split(',')))

        new_filter_list.append(new_filter_dict)

    return new_filter_list


