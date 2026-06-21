"""Menu endpoints — admin (PIN-gated) management + a public 'current menu'."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.menu import MenuCreate, MenuRead
from app.services import menus as menu_service

admin_router = APIRouter(
    prefix="/api/admin/menus",
    tags=["admin: menus"],
    dependencies=[Depends(require_admin)],
)


@admin_router.post("", response_model=MenuRead, status_code=status.HTTP_201_CREATED)
def create_menu(payload: MenuCreate, db: Session = Depends(get_db)) -> MenuRead:
    """Create this week's draft menu with its items."""
    menu = menu_service.create_menu(db, payload)
    return MenuRead.model_validate(menu)


@admin_router.get("", response_model=list[MenuRead])
def list_menus(db: Session = Depends(get_db)) -> list[MenuRead]:
    return [MenuRead.model_validate(m) for m in menu_service.list_menus(db)]


@admin_router.post("/{menu_id}/publish", response_model=MenuRead)
def publish_menu(menu_id: int, db: Session = Depends(get_db)) -> MenuRead:
    menu = menu_service.get_menu(db, menu_id)
    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found."
        )
    menu = menu_service.publish_menu(db, menu)
    return MenuRead.model_validate(menu)


public_router = APIRouter(prefix="/api/menus", tags=["menus"])


@public_router.get("/current", response_model=MenuRead)
def current_menu(db: Session = Depends(get_db)) -> MenuRead:
    """The active published menu — used by the order page and the parser."""
    menu = menu_service.current_published_menu(db)
    if menu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No published menu yet."
        )
    return MenuRead.model_validate(menu)
