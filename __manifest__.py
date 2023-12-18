{
    "name": "import_excel_stock",
    "summary": """
        Importacion de stocks
        """,
    "description": """
    """,
    "category": "Stock",
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": ["base","sale","stock"],
    # always loaded
    "data": [
        "views/warehouse.xml",
        "views/sale_order.xml",
    ],
    'license': 'LGPL-3',
}
