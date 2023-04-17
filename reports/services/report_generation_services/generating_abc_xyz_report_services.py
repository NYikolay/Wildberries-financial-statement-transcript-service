import datetime
from collections import defaultdict
from typing import Union, List

from django.db.models import QuerySet

from reports.services.report_generation_services.generate_period_filters_services import \
    generate_period_filter_conditions
from reports.services.report_generation_services.generating_report_db_data_service import \
    get_calculated_financials_by_products, get_nm_ids_revenues_by_weeks
from reports.services.report_generation_services.generating_sum_aggregation_objs_service import \
    get_financials_annotation_objects

import pandas as pd
import numpy as np


def get_past_months_filters() -> dict:
    """
    The function generates dictionaries containing the last 12 weeks and the year to which they refer
    :return:
    """
    last_year: datetime = datetime.date.today() - datetime.timedelta(days=365)
    weeks_by_years: dict = defaultdict(set)

    weeks_by_years_2: List[dict] = []

    for i in range(52):
        current_date = last_year + datetime.timedelta(weeks=i)
        year, week_num, _ = current_date.isocalendar()
        weeks_by_years[year].add(week_num)
        weeks_by_years_2.append({
            'year': year,
            'week_num': week_num
        })

    new_filter_list = [
        {
            'year': int(year),
            'week_nums': sorted(weeks_by_years[year])
        } for year in weeks_by_years
    ]

    filters = generate_period_filter_conditions(new_filter_list)

    return {
        'filters': filters,
        'weeks_by_years': pd.DataFrame(weeks_by_years_2)
    }


def get_abc_group(row):
    group = 'A' if row['increasing_proportion'] <= 80 else 'B' if 80 < row['increasing_proportion'] <= 95 else 'C'
    return group


def remove_zeros(group):
    nonzero_indices = lambda arr: np.where(arr)[0]
    revenues = group['revenue_by_article'].to_numpy()
    indices = nonzero_indices(revenues)
    return group.iloc[indices[0]:indices[-1]+1] if len(indices) > 0 else pd.DataFrame(columns=group.columns)


def get_xyz_group(row):
    group = 'X' if row['coefficient_xyz'] <= 10 else 'Y' if 25 >= row['coefficient_xyz'] > 10 else 'Z'
    return group


def generate_abc_report_values(calculated_financials_by_products: QuerySet) -> dict:
    """
    The function generates ABC report data based on the financial report for unique items request.user
    :param calculated_financials_by_products: QuerySet containing the financial report request.user for each unique item
    :return: Returns the dictionary. Containing:
    1. total_abc_dict - Final ABC report for processing in the template
    2. current_barcodes - A list containing the unique nm_ids by barcodes of the user
    3. calculated_abc_values_by_products - Supplemented financial report by unique nm_id request.user.
    Added increasing_proportion, group_abc
    """

    # Sort descending by share_in_revenue field
    calculated_values_by_products: pd.DataFrame = pd.DataFrame(
        calculated_financials_by_products).sort_values('share_in_revenue', ascending=False)

    # Calculation of the cumulative total by the share_in_revenue field and
    # recording in a separate column - increasing_proportion
    calculated_values_by_products[
        'increasing_proportion']: pd.DataFrame = calculated_values_by_products.loc[:, 'share_in_revenue'].cumsum()

    # Calculating the group nm_id based on the increasing_proportion column
    # and writing it to a separate column called group_abc
    calculated_values_by_products['group_abc'] = calculated_values_by_products.apply(
        get_abc_group, axis=1)

    source_abc_df = pd.DataFrame(
        [{'group_abc': 'A', 'revenue_by_article': 0, 'share_in_number': 0},
         {'group_abc': 'B', 'revenue_by_article': 0, 'share_in_number': 0},
         {'group_abc': 'C', 'revenue_by_article': 0, 'share_in_number': 0}]
    )
    # Aggregates data from DataFrame calculated_values_by_products with grouping by group_abc column and
    # creates a new DataFrame total_abc_df containing group_abc, revenue_by_article, share_in_number
    calculated_abc_df: pd.DataFrame = calculated_values_by_products.groupby('group_abc').agg({
        'revenue_by_article': 'sum',
        'share_in_number': 'sum'
    }).reset_index()[['group_abc', 'revenue_by_article', 'share_in_number']]

    total_abc_df = pd.merge(source_abc_df, calculated_abc_df, on='group_abc', how='outer')
    total_abc_df.drop(['revenue_by_article_x', 'share_in_number_x'], axis=1, inplace=True)
    total_abc_df.fillna(0, inplace=True)
    total_abc_df.rename(
        columns={'revenue_by_article_y': 'revenue_by_article', 'share_in_number_y': 'share_in_number'}, inplace=True)
    total_abc_df['revenue_by_article'] = total_abc_df['revenue_by_article'].round().astype(int)
    total_abc_df['share_in_number'] = total_abc_df['share_in_number'].round().astype(int)

    current_barcodes: List[int] = calculated_values_by_products.barcode.unique().tolist()

    return {
        "total_abc_dict": total_abc_df.to_dict('records'),
        "current_barcodes": current_barcodes,
        "calculated_abc_values_by_products": calculated_values_by_products
    }


def generate_xyz_report_values(
        current_user,
        current_api_key,
        sum_aggregation_objs_dict,
        current_barcodes
) -> pd.DataFrame:
    """
    The function generates an XYZ report based on the current_barcodes
    :param current_user: request.user
    :param current_api_key: active WebAPIKey of request.user
    :param sum_aggregation_objs_dict: Dictionary containing Coalesce(Sum()) objects
    in the value to filter values from the database
    :param current_barcodes: A list containing the unique barcode by nm_id of the current user from the SaleObject table
    :return: Returns the final XYZ report, which has the DataFrame data type
    """

    past_months_values: dict = get_past_months_filters()
    weeks_by_years: pd.DataFrame = past_months_values.get('weeks_by_years')
    revenues_by_weeks: pd.DataFrame = pd.DataFrame(get_nm_ids_revenues_by_weeks(
        current_user, current_api_key, current_barcodes, sum_aggregation_objs_dict, past_months_values.get('filters')
    ))

    index = pd.MultiIndex.from_product(
        [
            revenues_by_weeks['barcode'].unique(),
            weeks_by_years['year'].unique(),
            weeks_by_years['week_num'].unique()
        ],
        names=['barcode', 'year', 'week_num'])

    new_revenues_by_weeks_df: pd.DataFrame = pd.DataFrame(index=index).reset_index()

    # Combines new_revenues_by_weeks_df and revenues_by_weeks DataFrames. The result is a DataFrame where each unique
    # barcode by nm_id contains a row with the number of week and year for the last 12 months
    # (revenues of those weeks that do not have the original new_revenues_by_weeks_df is 0.0)
    new_revenues_by_weeks_df: pd.DataFrame = new_revenues_by_weeks_df.merge(
        revenues_by_weeks, how='left', on=['barcode', 'year', 'week_num']
    ).sort_values(['barcode', 'year', 'week_num']).fillna(0.0)

    groups = new_revenues_by_weeks_df.groupby('barcode', as_index=False)

    # At this point, the logic of trimming zeros at the edges for each unique barcode by nm_id works.
    # Conditionally if represented as a list. Source [0.0, 0.0, 123, 0.0, 1123, 0.0] --> result [123, 0.0, 1123]
    validated_revenues_by_weeks: pd.DataFrame = pd.concat(
        [remove_zeros(group) for _, group in groups], ignore_index=True)

    # The following 3 lines calculate the mean and standard deviation of the revenue_by_article column
    mean_std_df = validated_revenues_by_weeks.groupby('barcode').agg({'revenue_by_article': ['mean', 'std']})
    mean_std_df.columns = ['mean_revenue', 'std_revenue']
    mean_std_df = mean_std_df.reset_index()

    std_mean_df = pd.DataFrame(validated_revenues_by_weeks['barcode'].unique(), columns=['barcode'])
    std_mean_df = pd.merge(std_mean_df, mean_std_df, on='barcode', how='left')

    std_mean_df['coefficient_xyz'] = std_mean_df.apply(
        lambda row: 1000 if row['mean_revenue'] == 0 else (row['std_revenue'] / row['mean_revenue']) * 100,
        axis=1
    )

    std_mean_df['group'] = std_mean_df.apply(
        lambda row: 'X' if 0 <= row['coefficient_xyz'] <= 10 else 'Y' if 25 >= row['coefficient_xyz'] > 10 else 'Z',
        axis=1
    )

    # Removes all values where the std_revenue column has the value NaN.
    # Since goods with no standard deviation are not used in XYZ
    total_xyz_df: pd.DataFrame = std_mean_df.dropna(subset=['std_revenue']).reset_index(drop=True)

    return total_xyz_df


def make_abc_xyz_data_set(calculated_abc_values_by_products: pd.DataFrame, xyz_report: pd.DataFrame) -> dict:
    """
    The function returns the final result of the ABC XYZ analysis
    combines the DataFrames of ABC analysis and XYZ analysis.
    :param calculated_abc_values_by_products: The result of the generate_abc_report_values function,
    namely the DataFrame containing the financial report by unique nm_id with ABC analysis
    :param xyz_report: The result of the generate_xyz_report_values function,
    namely the DataFrame containing the financial report by unique nm_id with ABC analysis
    :return: Returns the dictionary containing:
    1. final_abc_xyz_df - dictionary, which contains a ready-made ABC XYZ analysis
    2. merged_abc_xyz_df - DataFrame, which contains unique nm_id after XYZ analysis is generated.
    It contains NOT ALL of the user's unique nm_id that is required for rendering in the template
    """
    merged_abc_xyz_df: pd.DataFrame = xyz_report.merge(calculated_abc_values_by_products)
    merged_abc_xyz_df['final_group'] = merged_abc_xyz_df.apply(
        lambda row: row['group_abc'] + row['group'],
        axis=1
    )

    final_abc_xyz_df = pd.DataFrame()
    final_abc_xyz_df['values'] = merged_abc_xyz_df.groupby('final_group').agg(
        {'revenue_by_article': 'sum'}
    ).round().astype(int)

    return {
        'final_abc_xyz_df': final_abc_xyz_df.to_dict(),
        'merged_abc_xyz_df': merged_abc_xyz_df
    }


def get_abc_xyz_report(
        current_user,
        current_api_key,
        filter_period_conditions: dict,
        sum_aggregation_objs_dict,
        net_costs_sum_aggregations_objs,
        total_revenue: float,
        total_products_count: int
) -> dict:
    """
    The function returns the calculated ABC XYZ analysis data. Calls the functions required for the calculations.
    :param current_user: request.user
    :param current_api_key: active WebAPIKey of request.user
    :param filter_period_conditions: Dictionary containing Q() objects in the value to filter values from the database:
    1. period
    2. subject_name
    3. brand_name
    :param sum_aggregation_objs_dict: Dictionary containing Coalesce(Sum()) objects
    in the value to filter values from the database
    :param net_costs_sum_aggregations_objs: Dictionary containing Coalesce(Sum()) objects in
    the value to filter values from the database
    :param total_revenue: Total revenue generated by
    reports.services.report_generation_services.get_total_financials_service.get_total_financials()
    :param total_products_count: Number of items received from SaleObject() model objects as a result of
    reports.services.report_generation_services.generating_report_db_data_service.get_report_db_inter_data
    :return: Dictionary containing the calculated values of ABC XYZ analysis
    """

    annotations_objs: dict = get_financials_annotation_objects()

    calculated_financials_by_products: Union[QuerySet, dict] = get_calculated_financials_by_products(
        current_user, current_api_key, filter_period_conditions,
        sum_aggregation_objs_dict, net_costs_sum_aggregations_objs,
        total_revenue, total_products_count, annotations_objs
    )

    abc_report: dict = generate_abc_report_values(calculated_financials_by_products)

    xyz_report: pd.DataFrame = generate_xyz_report_values(
        current_user, current_api_key, sum_aggregation_objs_dict, abc_report.get('current_barcodes')
    )

    abc_xyz_report: dict = make_abc_xyz_data_set(abc_report.get('calculated_abc_values_by_products'), xyz_report)

    final_products_values: pd.DataFrame = abc_report.get('calculated_abc_values_by_products').merge(
        abc_xyz_report.get('merged_abc_xyz_df'), how='left'
    ).replace(np.nan, None).sort_values('revenue_by_article', ascending=False)

    return {
        "products_calculated_values": final_products_values.to_dict('records'),
        "abc_xyz_report": abc_xyz_report.get('final_abc_xyz_df'),
        "abc_report": abc_report.get('total_abc_dict')
    }
