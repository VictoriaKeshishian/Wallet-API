from locust import HttpUser, task, between
import json
import random


class WalletUser(HttpUser):
    wait_time = between(1, 2)  # Время ожидания между запросами (1-2 секунды)

    # ID кошелька, который будет использоваться в тестах
    wallet_id = "ea75edb6-2d05-4b74-a476-4a1a08d80e27"

    @task
    def get_balance(self):
        response = self.client.get(f"/api/v1/wallets/{self.wallet_id}")
        if response.status_code != 200:
            print(f"Ошибка при получении баланса: {response.status_code} {response.text}")

    @task
    def deposit(self):
        amount = random.randint(1, 1000)  # Случайная сумма для пополнения
        response = self.client.post(f"/api/v1/wallets/{self.wallet_id}/operation",
                                     headers={"Content-Type": "application/json"},
                                     data=json.dumps({"operationType": "DEPOSIT", "amount": amount}))
        if response.status_code != 200:
            print(f"Ошибка при пополнении кошелька: {response.status_code} {response.text}")

    @task
    def withdraw(self):
        # Получаем баланс
        balance_response = self.client.get(f"/api/v1/wallets/{self.wallet_id}")
        if balance_response.status_code == 200:
            balance = balance_response.json().get('balance', 0)
            amount = random.randint(1, 1000)
            if amount <= balance:
                response = self.client.post(f"/api/v1/wallets/{self.wallet_id}/operation",
                                            headers={"Content-Type": "application/json"},
                                            data=json.dumps({"operationType": "WITHDRAW", "amount": amount}))
                if response.status_code != 200:
                    print(f"Ошибка при снятии с кошелька: {response.status_code} {response.text}")
            else:
                print("Недостаточно средств для снятия.")
        else:
            print(f"Ошибка при получении баланса: {balance_response.status_code} {balance_response.text}")

# Запуск Locust с командой: locust --host=http://localhost:8000
