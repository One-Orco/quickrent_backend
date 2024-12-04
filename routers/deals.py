from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, models, crud
from database import get_db
from auth import get_current_active_user
from typing import Optional
from fastapi import File, UploadFile
import shutil
router = APIRouter()

@router.post("/deals/", response_model=schemas.Deal)
def create_deal_for_agent(
    deal: schemas.DealCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "agent":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.create_deal(db=db, deal=deal, agent_id=current_user.id)

@router.get("/deals/", response_model=list[schemas.Deal])
def read_deals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role == "admin":
        # Admin can view all deals
        return crud.get_deals(db, skip=skip, limit=limit)
    elif current_user.role == "agent":
        # Agent can only view their own deals
        return crud.get_deals_by_agent(db, agent_id=current_user.id, skip=skip, limit=limit)
    else:
        raise HTTPException(status_code=403, detail="Operation not permitted")



@router.post("/deals/{deal_id}/approve", response_model=schemas.Deal)
@router.post("/deals/{deal_id}/approve", response_model=schemas.Deal)
def approve_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    deal = crud.update_deal_status(db, deal_id=deal_id, status="approved")
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

@router.post("/deals/{deal_id}/decline", response_model=schemas.Deal)
def decline_deal(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    deal = crud.update_deal_status(db, deal_id=deal_id, status="declined")
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal




@router.get("/deals/", response_model=list[schemas.Deal])
def read_filtered_deals(
    property_type: Optional[str] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    return crud.get_filtered_deals(
        db,
        current_user=current_user,
        property_type=property_type,
        transaction_type=transaction_type,
        status=status,
        location=location,
        min_price=min_price,
        max_price=max_price
    )
@router.post("/deals/{deal_id}/upload-document/")
async def upload_document(
    deal_id: int,
    file: UploadFile = File(...),
    file_type: str = "",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    # Ensure only the agent associated with the deal can upload
    deal = db.query(models.Deal).filter(models.Deal.id == deal_id, models.Deal.agent_id == current_user.id).first()
    if not deal:
        raise HTTPException(status_code=403, detail="Operation not permitted")

    # Save the uploaded file
    file_location = f"uploads/{deal_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Add file details to the database
    document = models.DealDocument(deal_id=deal_id, file_type=file_type, file_path=file_location)
    db.add(document)
    db.commit()

    return {"message": "File uploaded successfully", "file_path": file_location}


@router.get("/realtor/deals/", response_model=list[schemas.Deal])
def get_pending_deals_for_realtor(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "realtor":
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return db.query(models.Deal).filter(models.Deal.status == "pending_realtor").all()
@router.post("/realtor/deals/{deal_id}/approve", response_model=schemas.Deal)
def approve_deal_by_realtor(
    deal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    if current_user.role != "realtor":
        raise HTTPException(status_code=403, detail="Operation not permitted")

    deal = db.query(models.Deal).filter(models.Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if deal.status != "pending_realtor":
        raise HTTPException(status_code=400, detail="Deal not in pending_realtor status")

    deal.status = "pending_admin"  # Forward to admin for final approval
    db.commit()
    db.refresh(deal)
    return deal
