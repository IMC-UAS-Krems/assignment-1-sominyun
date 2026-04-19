"""
users.py
--------
Implement the class hierarchy for platform users.

Classes to implement:
  - User (base class)
    - FreeUser
    - PremiumUser
    - FamilyAccountUser
    - FamilyMember
"""
from __future__ import annotations
from datetime import date


class User:
    def __init__(self, user_id: str, name: str, age: int):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []

    def add_session(self, session):
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(s.duration_listened_seconds for s in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60.0

    def unique_tracks_listened(self) -> set[str]:
        return {s.track.track_id for s in self.sessions}


class FreeUser(User):
    def __init__(self, user_id: str, name: str, age: int):
        super().__init__(user_id, name, age)
        self.MAX_SKIPS_PER_HOUR = 6


class PremiumUser(User):
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date):
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start


class FamilyAccountUser(User):
    def __init__(self, user_id: str, name: str, age: int):
        super().__init__(user_id, name, age)
        self.sub_users: list[FamilyMember] = []

    def add_sub_user(self, sub_user: FamilyMember) -> None:
        if sub_user not in self.sub_users:
            self.sub_users.append(sub_user)

    def all_members(self) -> list[User]:
        return [self] + self.sub_users


class FamilyMember(User):
    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser, ):
        super().__init__(user_id, name, age)
        self.parent = parent
