from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, UUID4, ConfigDict, field_validator
from sqlalchemy.orm import Session
from app.models import Wallet, Base
from app.database import get_db
import logging
from logging.handlers import RotatingFileHandler

app = FastAPI()

# Настройка логирования
log_file = 'app.log'
handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


# Pydantic модель для ответа
class WalletResponse(BaseModel):
    id: UUID4
    balance: float

    model_config = ConfigDict(from_attributes=True)


class Operation(BaseModel):
    operationType: str  # "DEPOSIT" или "WITHDRAW"
    amount: float

    @field_validator('operationType')
    def validate_operation_type(cls, value):
        if value not in {"DEPOSIT", "WITHDRAW"}:
            raise ValueError('Operation type must be "DEPOSIT" or "WITHDRAW"')
        return value

    @field_validator('amount')
    def validate_amount(cls, value):
        if value <= 0:
            raise ValueError('Amount must be greater than zero')
        return value


# Эндпоинт для операций с блокировкой строки
@app.post("/api/v1/wallets/{wallet_id}/operation")
async def operation(wallet_id: UUID4, operation: Operation, db: Session = Depends(get_db)):
    try:
        wallet = db.query(Wallet).filter(Wallet.id == wallet_id).with_for_update().first()

        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # Валидация происходит в классе Operation
        if operation.operationType == "DEPOSIT":
            wallet.balance += operation.amount
        elif operation.operationType == "WITHDRAW":
            if wallet.balance < operation.amount:
                logger.error(f"Insufficient funds for wallet {wallet_id}. Current balance: {wallet.balance}, requested amount: {operation.amount}")
                raise HTTPException(status_code=409, detail="Insufficient funds")
            wallet.balance -= operation.amount

        db.commit()
        return {"message": "Operation successful", "balance": wallet.balance}

    except HTTPException as e:
        logger.warning(f"HTTPException occurred: {e.detail}")
        raise e

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Эндпоинт для получения баланса
@app.get("/api/v1/wallets/{wallet_id}", response_model=WalletResponse)
async def get_balance(wallet_id: UUID4, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet


# Эндпоинт для создания нового кошелька
@app.post("/api/v1/wallets", response_model=WalletResponse)
async def create_wallet(db: Session = Depends(get_db)):
    try:
        new_wallet = Wallet(balance=0)
        db.add(new_wallet)
        db.commit()
        db.refresh(new_wallet)
        return new_wallet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


