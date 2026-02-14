from nestipy.common import Module
from nestipy.web import (
    ActionsModule,
    ActionsOption,
    OriginActionGuard,
    CsrfActionGuard,
)

from app_controller import AppController
from app_service import AppService
from app_actions import AppActions


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[
                    OriginActionGuard(
                        allowed_origins=[
                            "http://localhost:2345",
                            "http://127.0.0.1:2345",
                        ]
                    ),
                    CsrfActionGuard(),
                ],
            )
        )
    ],
    controllers=[AppController],
    providers=[AppService, AppActions],
)
class AppModule: ...