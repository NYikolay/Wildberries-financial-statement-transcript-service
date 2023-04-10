from typing import List


def get_period_filter_data(filter_dict: dict) -> dict:
    new_filter_list: List[dict] = []
    current_filters_names = set()

    for dict_values in filter_dict:

        new_filter_dict: dict = dict()
        if dict_values == 'subject_name':
            new_filter_dict['subject_name'] = list(map(str, filter_dict[dict_values][0].split(',')))
            current_filters_names.add('subject_name')
        elif dict_values == 'brand_name':
            new_filter_dict['brand_name'] = list(map(str, filter_dict[dict_values][0].split(',')))
            current_filters_names.add('brand_name')
        else:
            new_filter_dict['year'] = int(dict_values)
            new_filter_dict['week_nums'] = list(map(int, filter_dict[dict_values][0].split(',')))
            current_filters_names.add('year')
            current_filters_names.add('week_nums')
        new_filter_list.append(new_filter_dict)

    return {
        'new_filter_list': new_filter_list,
        'current_filters_names': current_filters_names
    }
