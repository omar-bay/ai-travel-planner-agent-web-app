from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..dependencies.auth import get_db, get_current_user
from ..models import SavedTrip
from ..schemas.trip import SaveTripIn, TripOut


router = APIRouter(prefix="/api", tags=["trips"])


@router.post("/save-trip", response_model=TripOut, status_code=201)
async def save_trip(payload: SaveTripIn, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    trip = SavedTrip(user_id=user.id, city=payload.city, recommendation=payload.recommendation)
    db.add(trip)
    await db.commit()
    await db.refresh(trip)
    return trip


@router.get("/saved-trips", response_model=list[TripOut])
async def list_trips(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(SavedTrip).where(SavedTrip.user_id == user.id).order_by(SavedTrip.created_at.desc()))
    trips = result.scalars().all()
    return trips


@router.delete("/saved-trips/{trip_id}", status_code=204)
async def delete_trip(trip_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    result = await db.execute(select(SavedTrip).where(SavedTrip.id == trip_id, SavedTrip.user_id == user.id))
    trip = result.scalar_one_or_none()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    await db.execute(delete(SavedTrip).where(SavedTrip.id == trip_id))
    await db.commit()
    return