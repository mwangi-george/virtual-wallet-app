from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    admin_router,
    auth_router,
    wallet_router,
    analytics_router,
    user_router,
)

# Allowed frontends will be specified here
origins = [
    "http://localhost:3000",
]


def create_app_entrypoint() -> FastAPI:
    """ Create FastAPI app entry point """

    app = FastAPI(
        title="Virtual Wallet System",
        description=f"A backend service that enables users to manage their finances by depositing, "
                    f"transferring, and withdrawing funds. Coupled with spending analytics, "
                    f"this system categorizes expenses and provides insights to help users track "
                    f"and manage their money more effectively.",
        version="1.0.1",
        contact={
            "name": "Mwangi George",
            "email": "mwangigeorge648@gmail.com",
        },
        license_info={
            "name": "Licence",
            "url": "https://opensource.org/licenses/MIT",
        }
    )

    # Configure Cross Origin Resource Sharing
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the routers to the entry point
    app.include_router(auth_router())
    app.include_router(wallet_router())
    app.include_router(analytics_router())
    app.include_router(user_router())
    app.include_router(admin_router())

    return app


# instantiate the app
app = create_app_entrypoint()
