from strawberry.types import Info
from nestipy.common.decorator import Inject
from nestipy.plugins.strawberry_module.decorator import Resolver, Query, Mutation
from .invoice_input import InvoiceInput
from .invoice_service import InvoiceService


@Resolver()
class InvoiceResolver:

    invoice_service: InvoiceService = Inject(InvoiceService)

    @Query()
    async def invoice_test_query(self, root: Info) -> str:
        return await self.invoice_service.list()

    @Mutation()
    async def invoice_test_mutation(self, root: Info, data: InvoiceInput) -> str:
        return data.test