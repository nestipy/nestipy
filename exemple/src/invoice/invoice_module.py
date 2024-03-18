from nestipy.common.decorator import Module

from .invoice_service import InvoiceService
from .invoice_resolver import InvoiceResolver


@Module(
    providers=[
        InvoiceService,
        InvoiceResolver
    ],
)
class InvoiceModule:
    ...
