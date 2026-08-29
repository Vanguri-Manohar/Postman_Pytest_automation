from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# ==========================================
# 1. DATABASE SETUP
# ==========================================
# This will create a local file named "local_database.db" in your folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./local_database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. SQL TABLE STRUCTURE
# ==========================================
class DBItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

# Instruct SQLite to actually create the table
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. API DATA MODELS (What we expect to receive)
# ==========================================
class ItemCreate(BaseModel):
    name: str
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    model_config = {"from_attributes": True}

# ==========================================
# 4. FASTAPI APP & ENDPOINTS
# ==========================================
app = FastAPI(title="Local Database API")

# Helper function to open/close database connections safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Saves a new item to the SQLite database."""
    new_item = DBItem(name=item.name, price=item.price)
    db.add(new_item)
    db.commit()          # Commits the save to the hard drive
    db.refresh(new_item) # Assigns the new ID
    return new_item

@app.get("/items/", response_model=list[ItemResponse], status_code=200)
def get_items(db: Session = Depends(get_db)):
    """Fetches all items currently saved in the database."""
    return db.query(DBItem).all()