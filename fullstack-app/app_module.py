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
                            "http://localhost:5173",
                            "http://127.0.0.1:5173",
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