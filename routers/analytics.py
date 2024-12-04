from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud, models
from database import get_db
from auth import get_current_active_user

router = APIRouter()

@router.get("/admin/analytics/")
def get_admin_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")

    return {
        "total_deals_by_status": crud.get_total_deals_by_status(db),
        "top_performing_agents": crud.get_top_performing_agents(db),
        "most_popular_property_types": crud.get_most_popular_property_types(db),
        "deals_by_location": crud.get_deals_by_location(db),
        "total_earnings": crud.get_total_earnings(db),
    }
