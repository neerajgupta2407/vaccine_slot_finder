from dataclasses import dataclass
from typing import List


@dataclass
class SessionObject:
    session_id: str
    date: str
    available_capacity: int
    min_age_limit: int
    vaccine: str
    slots: List[str]

    @property
    def is_available(self):
        return self.available_capacity > 0

    @property
    def is_18(self):
        return self.min_age_limit == 18

    @property
    def is_45(self):
        return self.min_age_limit == 45

    @property
    def display_info_str(self):
        return f"{self.date}:  {self.vaccine} -> Available:{self.available_capacity}"


@dataclass(init=False)
class CenterObject:
    center_id: int
    name: str
    address: str
    state_name: str
    district_name: str
    block_name: str
    pincode: int
    lat: int
    long: int
    _from: str
    to: str
    fee_type: str
    sessions: List[SessionObject]

    def __init__(self, **kwargs):
        kwargs["_from"] = kwargs["from"]
        del kwargs["from"]
        self._from = kwargs["_from"]

        for a in kwargs:
            setattr(self, a, kwargs[a])
        self.sessions = [SessionObject(**b) for b in kwargs["sessions"]]

    @property
    def available_18_sessions(self):
        return [a for a in self.sessions if a.is_18 and a.is_available]

    @property
    def is_18_session_available(self):
        return len(self.available_18_sessions) > 0

    @property
    def available_45_sessions(self):
        return [a for a in self.sessions if a.is_45 and a.is_available]

    @property
    def is_45_session_available(self):
        return len(self.available_45_sessions) > 0

    @property
    def detail_available_18_info_str(self):
        text = f"{self.pincode} {self.name} {self.address}\n"
        for a in self.available_18_sessions:
            text += a.display_info_str + "\n"
        return text

    @property
    def detail_available_45_info_str(self):
        text = f"{self.pincode} {self.name} {self.address}\n"
        for a in self.available_45_sessions:
            text += a.display_info_str + "\n"
        return text
