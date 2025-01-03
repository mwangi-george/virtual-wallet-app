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
    """
    Create and configure the FastAPI application entry point.

    This function initializes the FastAPI application with the following features:
    - **Metadata**: Provides application title, description, version, and contact/license information.
    - **CORS Middleware**: Configures Cross-Origin Resource Sharing (CORS) to allow all origins, methods, headers,
      and credentials for maximum compatibility.
    - **Routers**: Includes the following routers:
        - `auth_router`: Handles authentication-related routes.
        - `wallet_router`: Manages wallet-related functionality (e.g., deposits, withdrawals, and transfers).
        - `analytics_router`: Provides spending analytics and expense categorization routes.
        - `user_router`: Handles user-specific routes.
        - `admin_router`: Manages administrative routes.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """

    entry_point = FastAPI(
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
    entry_point.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the routers to the entry point
    entry_point.include_router(auth_router())
    entry_point.include_router(wallet_router())
    entry_point.include_router(analytics_router())
    entry_point.include_router(user_router())
    entry_point.include_router(admin_router())

    return entry_point


# instantiate the app
app = create_app_entrypoint()
