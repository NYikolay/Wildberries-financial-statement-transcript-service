from django.db.models import FloatField, F, Value, Case, When, ExpressionWrapper
from django.db.models.functions import Coalesce


def get_retail_revenue_formula_annotation_obj():
    retail_revenue_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('retail_sales_sum') - F('retail_storno_sales_sum') + F('retail_correct_sales_sum') -
            F('retail_return_sum') + F('retail_storno_returns_sum') - F('retail_correct_returns_sum') +
            F('retail_marriage_payment_sum') + F('retail_sales_payment_lost_marriage_sum') -
            F('retail_returns_payment_lost_marriage_sum') +
            F('retail_partial_compensation_marriage_sum') +
            F('retail_sales_advance_payment_goods_without_payment_sum') -
            F('retail_returns_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return retail_revenue_annotation_obj


def get_revenue_formula_annotation_obj():
    revenue_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('sales_sum') - F('storno_sales_sum') + F('correct_sales_sum') -
            F('returns_sum') + F('storno_returns_sum') - F('correct_returns_sum') +
            F('marriage_payment_sum') + F('sales_payment_lost_marriage_sum') -
            F('returns_payment_lost_marriage_sum') +
            F('partial_compensation_marriage_sum') +
            F('sales_advance_payment_goods_without_payment_sum') -
            F('returns_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return revenue_annotation_obj


def get_share_in_revenue_formula_annotation_obj():
    share_in_revenue_annotation_obj = Coalesce(Case(
        When(total_revenue__gt=0, then=((F('revenue_by_article') / F('total_revenue')) * 100)),
        default=Value(0.0),
        output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return share_in_revenue_annotation_obj


def get_sales_quantity_formula_annotation_obj():
    sales_quantity_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('sales_quantity_sum') - F('strono_sales_quantity_sum') + F('correct_sales_quantity_sum') +
            F('marriage_payment_quantity_sum') + F('sales_payment_lost_marriage_quantity_sum') -
            F('returns_payment_lost_marriage_quantity_sum') + F('partial_compensation_marriage_quantity_sum') +
            F('sales_advance_payment_goods_without_payment_quantity_sum') -
            F('returns_advance_payment_goods_without_payment_quantity_sum'),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return sales_quantity_annotation_obj


def get_returns_quantity_formula_annotation_obj():
    returns_quantity_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('returns_quantity_sum') + F('strono_returns_quantity_sum') - F('correct_return_quantity_sum'),
            output_field=FloatField()
        ),
        Value(0.0),
        output_field=FloatField()
    )

    return returns_quantity_annotation_obj


def get_commission_formula_annotation_obj():
    commission_annotation_obj = Coalesce(
        ExpressionWrapper(
            (
                    F('sales_sum') -
                    F('storno_sales_sum') +
                    F('correct_sales_sum') -
                    F('returns_sum') +
                    F('storno_returns_sum') -
                    F('correct_returns_sum') +
                    F('marriage_payment_sum') +
                    F('sales_payment_lost_marriage_sum') -
                    F('returns_payment_lost_marriage_sum') +
                    F('partial_compensation_marriage_sum') +
                    F('sales_advance_payment_goods_without_payment_sum') -
                    F('returns_advance_payment_goods_without_payment_sum')
            ) -
            (
                    F('commission_sales_sum') -
                    F('commission_storno_sales_sum') +
                    F('commission_correct_sales_sum') -
                    F('commission_returns_sum') +
                    F('commission_storno_returns_sum') -
                    F('commission_correct_returns_sum') +
                    F('commission_marriage_payment_sum') +
                    F('commission_sales_payment_lost_marriage_sum') -
                    F('commission_returns_payment_lost_marriage_sum') +
                    F('commission_partial_compensation_marriage_sum') +
                    F('commission_sales_advance_payment_goods_without_payment_sum') -
                    F('commission_returns_advance_payment_goods_without_payment_sum')
            ) -
            (F('commission_reimbursement_of_transportation_costs') + F('commission_overstatement_of_logistics_costs')),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField(),
    )

    return commission_annotation_obj


def get_net_costs_formula_annotation_obj():
    net_costs_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('net_cost_sale_sum') - F('net_cost_storno_sale_sum') + F('net_cost_correct_sale_sum') -
            F('net_cost_return_sum') + F('net_cost_strono_returns_sum') - F('net_cost_correct_return_sum') +
            F('net_cost_marriage_payment_sum') + F('net_cost_sales_payment_lost_marriage_sum') -
            F('net_cost_returns_payment_lost_marriage_sum') + F('net_cost_partial_compensation_marriage_sum') +
            F('net_cost_sales_advance_payment_goods_without_payment_sum') -
            F('net_cost_returns_advance_payment_goods_without_payment_sum'),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return net_costs_annotation_obj


def get_marginality_formula_annotation_obj():
    marginality_annotation_obj = Coalesce(Case(
        When(net_costs_sum__gt=0, then=((F('revenue_by_article') - F('net_costs_sum')) / F('revenue_by_article')) * 100),
        default=Value(0.0), output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return marginality_annotation_obj


def get_share_in_number_formula_annotation_obj():
    share_in_number_annotation_obj = Coalesce(Case(
        When(total_products_count__gt=0, then=((1 / F('total_products_count')) * 100)),
        default=Value(0.0),
        output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return share_in_number_annotation_obj


def get_total_payable_formula_annotation_obj():
    total_payable_annotation_obj = Coalesce(
        ExpressionWrapper(
            F('interim_revenue') - F('commission') -
            F('logistic_sum') - F('penalty_sum') -
            F('additional_payment_sum') - F('net_costs_sum'),
            output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return total_payable_annotation_obj


def get_rom_formula_annotation_obj():
    rom_annotations_obj = Coalesce(Case(
        When(net_costs_sum__gt=0, then=((F('total_payable') / F('net_costs_sum')) * 100)),
        default=Value(0.0), output_field=FloatField()),
        Value(0.0),
        output_field=FloatField()
    )

    return rom_annotations_obj

