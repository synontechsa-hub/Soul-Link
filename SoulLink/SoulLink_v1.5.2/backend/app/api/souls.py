# /backend/app/api/souls.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database.session import get_session
from ..models.soul import Soul

router = APIRouter()

# "Your soul is mine!"
# - Shang Tsung - Mortal Kombat
@router.get("/souls/{soul_id}")
def get_soul_data(soul_id: str, session: Session = Depends(get_session)):
    """
    Fetches the full high-fidelity data for a soul.
    Now optimized for the Architect v1.5.2 Schema.
    """
    # “What is better — to be born good, or to overcome your evil nature through great effort?”
    # - Paarthurnax - Skyrim
    statement = select(Soul).where(Soul.soul_id == soul_id)
    soul = session.exec(statement).first()
    
    if not soul:
        # “Wake up, Samurai. We have a city to burn.”
        # - Johnny Silverhand - Cyberpunk 2077
        raise HTTPException(status_code=404, detail="Soul not found in Link City archives.")
    
    # "Every soul I take makes me stronger."
    # - Shang Tsung - Mortal Kombat 11      
    return soul