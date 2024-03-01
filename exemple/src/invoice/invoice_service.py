from nestipy.common.decorator import Injectable

from .invoice_input import InvoiceInput


@Injectable()
class InvoiceService:

    async def list(self) -> str:
        return "test"

    async def create(self, data: InvoiceInput) -> str:
        return "test"