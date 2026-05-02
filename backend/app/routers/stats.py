from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_store_id
from backend.app.core.subscription import check_subscription_active
from backend.app.schemas.stats import StatsSummary
from backend.app.services import stats as stats_service

router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)

@router.get("/summary", response_model=StatsSummary)
def get_summary(
    db: Session = Depends(get_db),
    store_id: int = Depends(check_subscription_active)
):
    """Retorna KPIs filtrados por la tienda autenticada."""
    return stats_service.get_dashboard_summary(db, store_id=store_id)
