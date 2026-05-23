from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hackathon_judge.db.engine import get_db
from hackathon_judge.db.models import HardRule, Rubric
from hackathon_judge.schemas.rubric import HardRuleCreate, HardRuleOut, RubricCreate, RubricOut, RubricUpdate

router = APIRouter(prefix="/api", tags=["rubrics"])


@router.get("/hackathons/{hackathon_id}/rubrics", response_model=list[RubricOut])
async def list_rubrics(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rubric).where(Rubric.hackathon_id == hackathon_id))
    return list(result.scalars().all())


@router.post("/hackathons/{hackathon_id}/rubrics", response_model=RubricOut)
async def create_rubric(hackathon_id: int, body: RubricCreate, db: AsyncSession = Depends(get_db)):
    r = Rubric(hackathon_id=hackathon_id, **body.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.put("/rubrics/{rubric_id}", response_model=RubricOut)
async def update_rubric(rubric_id: int, body: RubricUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rubric).where(Rubric.id == rubric_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Rubric not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(r, k, v)
    await db.commit()
    await db.refresh(r)
    return r


@router.delete("/rubrics/{rubric_id}")
async def delete_rubric(rubric_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rubric).where(Rubric.id == rubric_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Rubric not found")
    await db.delete(r)
    await db.commit()
    return {"message": "Deleted"}


@router.get("/hackathons/{hackathon_id}/hard-rules", response_model=list[HardRuleOut])
async def list_hard_rules(hackathon_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HardRule).where(HardRule.hackathon_id == hackathon_id))
    return list(result.scalars().all())


@router.post("/hackathons/{hackathon_id}/hard-rules", response_model=HardRuleOut)
async def create_hard_rule(hackathon_id: int, body: HardRuleCreate, db: AsyncSession = Depends(get_db)):
    r = HardRule(hackathon_id=hackathon_id, **body.model_dump())
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.delete("/hard-rules/{rule_id}")
async def delete_hard_rule(rule_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(HardRule).where(HardRule.id == rule_id))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Hard rule not found")
    await db.delete(r)
    await db.commit()
    return {"message": "Deleted"}
