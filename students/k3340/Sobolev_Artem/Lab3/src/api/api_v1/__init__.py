from fastapi import APIRouter

from .auth import router as auth_router
from .books import router as books_router
from .exchange_requests import router as exchange_requests_router
from .genres import router as genres_router
from .authors import router as authors_router
from .library import router as library_router
from .parser import router as parser_router
from .profiles import router as profiles_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(genres_router)
router.include_router(authors_router)
router.include_router(books_router)
router.include_router(users_router)
router.include_router(profiles_router)
router.include_router(library_router)
router.include_router(exchange_requests_router)
router.include_router(parser_router)
