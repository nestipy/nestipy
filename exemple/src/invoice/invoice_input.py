from nestipy.plugins.strawberry_module.decorator import Input


@Input()
class InvoiceInput:
    test: str