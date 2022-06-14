import pytest

class BankAccount:
    def __init__(self, starting_balance: int = 50):
        self.balance: int = starting_balance
    
    def deposit(self, amount: int):
        if amount <= 0:
            raise Exception('Add a higher amount.')
        self.balance += amount
        return self
    
    def withdraw(self, amount: int):
        if amount > self.balance:
            raise Exception('Insufficient funds in account.')
        self.balance -= amount
        return self
    
    def collect_interest(self):
        self.balance *= 1.1
        return self