from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import AsyncSessionLocal, engine, Base
from . import models, schemas, auth

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


# ---------------- Login ----------------
@app.post("/login")
async def login(data: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ---------------- Create Item ----------------
@app.post("/items")
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    new_item = models.Item(**item.model_dump())
    db.add(new_item)
    await db.commit()
    return new_item


# ---------------- Receive ----------------
@app.post("/receive")
async def receive(data: schemas.MovementCreate, db: AsyncSession = Depends(get_db)):
    item = await db.get(models.Item, data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.quantity += data.quantity
    movement = models.StockMovement(item_id=data.item_id, type="RECEIVE", quantity=data.quantity)
    db.add(movement)
    await db.commit()
    return {"message": "Received successfully"}


# ---------------- Issue ----------------
@app.post("/issue")
async def issue(data: schemas.MovementCreate, db: AsyncSession = Depends(get_db)):
    item = await db.get(models.Item, data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.quantity < data.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    item.quantity -= data.quantity
    movement = models.StockMovement(item_id=data.item_id, type="ISSUE", quantity=data.quantity)
    db.add(movement)
    await db.commit()
    return {"message": "Issued successfully"}


# ---------------- Balance ----------------
@app.get("/balance/{item_id}")
async def balance(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await d
