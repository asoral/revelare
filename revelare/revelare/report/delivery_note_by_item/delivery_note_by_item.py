# Copyright (c) 2019, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub

def execute(filters=None):
    columns = get_columns()

    if (filters.customer):
        datos = get_specific_data(filters)
    else:
        datos = get_all_data(filters)

    # frappe.msgprint(_(str(type(filters.customer))))
    data = prepare_data(datos)
 
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Identificador"),
            "fieldname": "identificador",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Fecha"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Cliente"),
            "fieldname": "cliente",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("Codigo del Producto"),
            "fieldname": "codigo_producto",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100
        },
        {
            "label": _("Monto"),
            "fieldname": "monto",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Tarifa de la lista de precios"),
            "fieldname": "tarifa_lista",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 90
        },
        {
            "label": _("DIESEL"),
            "fieldname": "diesel",
            "fieldtype": "Float",
            "width": 90
        },
        {
            "label": _("REGULAR"),
            "fieldname": "regular",
            "fieldtype": "Float",
            "width": 90
        },
        {
            "label": _("SUPER"),
            "fieldname": "super",
            "fieldtype": "Float",
            "width": 90
        }
    ]

    return columns


def get_all_data(filters):

    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
                                            name, customer_name 
                                    FROM `tabDelivery Note`
                                    WHERE posting_date
                                    BETWEEN %(fecha_inicio)s AND %(fecha_final)s
                                    AND company=%(compa)s''', 
                                    {'fecha_inicio': str(filters.from_date),
                                     'fecha_final': str(filters.to_date),
                                     'compa': str(filters.company)}, as_dict=True)

    return delivery_note


def get_specific_data(filters):
    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
                                            name, customer_name 
                                    FROM `tabDelivery Note`
                                    WHERE posting_date
                                    BETWEEN %(fecha_inicio)s AND %(fecha_final)s
                                    AND customer_name=%(cliente)s AND company=%(compa)s''', 
                                    {'fecha_inicio': str(filters.from_date),
                                     'fecha_final': str(filters.to_date),
                                     'cliente': str(filters.customer),
                                     'compa': str(filters.company)}, as_dict=True)

    return delivery_note


def get_data_item(vale):
    delivery_note_item = frappe.db.get_values('Delivery Note Item',
                                        filters={'parent': vale},
                                        fieldname=['item_code', 'qty', 'amount', 'uom',
                                                  'rate'], as_dict=1)

    return delivery_note_item


def prepare_data(data_delivery_note):

    data = []

    for item_data in data_delivery_note:
        row = frappe._dict({
            'identificador': _(item_data.numero_vale_cliente),
            'posting_date': item_data.posting_date,
            'cliente': item_data.customer_name
            # "indent": flt(1)
        })

        item_info = get_data_item(item_data.name)
        row['codigo_producto'] = item_info[0]['item_code']
        row['monto'] = item_info[0]['amount']
        row['tarifa_lista'] = item_info[0]['rate']
        row['uom'] = item_info[0]['uom']
        # frappe.msgprint(_(str(item_info)))

        if 'DIESEL' in item_info[0]['item_code']:
            row['diesel'] = item_info[0]['qty']

        elif 'REGULAR' in item_info[0]['item_code']:
            row['regular'] = item_info[0]['qty']

        elif 'SUPER' in item_info[0]['item_code']:
            row['super'] = item_info[0]['qty']

        data.append(row)

    return data
