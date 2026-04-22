from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.stats import StatsSummary
from backend.app.services import stats as stats_service

router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)

@router.get("/summary", response_model=StatsSummary)
def get_summary(db: Session = Depends(get_db)):
    """
    Retorna los KPIs principales para nutrir el Dashboard central.
    Realiza las conmutaciones y conteos de inventario a nivel de Base de Datos.
    """
    return stats_service.get_dashboard_summary(db)
