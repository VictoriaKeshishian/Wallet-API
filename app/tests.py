from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Wallet
import uuid

client = TestClient(app)

# Настраиваем тестовую базу данных (используем SQLite для тестов)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Функция для создания тестового кошелька
def create_test_wallet(balance=0.0):
    db = TestingSessionLocal()
    wallet = Wallet(balance=balance)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    db.close()
    return wallet


def test_deposit_wallet_not_found():
    random_wallet_id = uuid.uuid4()  # Генерируем новый UUID
    response = client.post(f"/api/v1/wallets/{random_wallet_id}/operation", json={"operationType": "DEPOSIT", "amount": 1000})
    print(response.json())  # Вывод тела ответа для отладки
    assert response.status_code == 404
    assert response.json() == {"detail": "Wallet not found"}


def test_deposit_success():
    # Создаем тестовый кошелек
    wallet = create_test_wallet()

    # Успешное пополнение
    response = client.post(f"/api/v1/wallets/{wallet.id}/operation", json={"operationType": "DEPOSIT", "amount": 1000})
    assert response.status_code == 200
    assert response.json() == {"message": "Operation successful", "balance": 1000.0}


def test_withdraw_success():
    # Создаем тестовый кошелек с балансом 2000
    wallet = create_test_wallet(balance=2000)

    # Успешное снятие
    response = client.post(f"/api/v1/wallets/{wallet.id}/operation", json={"operationType": "WITHDRAW", "amount": 1000})
    assert response.status_code == 200
    assert response.json() == {"message": "Operation successful", "balance": 1000.0}


def test_withdraw_insufficient_funds():
    # Создаем тестовый кошелек с балансом 500
    wallet = create_test_wallet(balance=500)

    # Недостаточно средств
    response = client.post(f"/api/v1/wallets/{wallet.id}/operation", json={"operationType": "WITHDRAW", "amount": 1000})
    assert response.status_code == 409
    assert response.json() == {"detail": "Insufficient funds"}


def test_get_balance():
    # Создаем тестовый кошелек с балансом 3000
    wallet = create_test_wallet(balance=3000)

    # Проверяем баланс кошелька
    response = client.get(f"/api/v1/wallets/{wallet.id}")
    assert response.status_code == 200
    assert response.json() == {"id": str(wallet.id), "balance": 3000.0}


def test_invalid_operation_type():
    # Создаем тестовый кошелек
    wallet = create_test_wallet()

    # Неверный тип операции
    response = client.post(f"/api/v1/wallets/{wallet.id}/operation", json={"operationType": "INVALID", "amount": 1000})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid operation type"}


def test_invalid_json():
    # Создаем тестовый кошелек
    wallet = create_test_wallet()

    # Некорректный JSON
    response = client.post(f"/api/v1/wallets/{wallet.id}/operation", json={"operationType": "DEPOSIT"})
    assert response.status_code == 422  # Ошибка валидации Pydantic

