from dataclasses import dataclass
from typing import List

from vaccine_slots.settings import MIN_SLOTS


class FeeType:
    free = "free"
    paid = "paid"


@dataclass
class StateObject:
    state_id: int
    state_name: str


@dataclass
class DistrictObject:
    district_id: int
    district_name: str


@dataclass
class SessionObject:
    session_id: str
    date: str
    available_capacity: int
    min_age_limit: int
    vaccine: str
    slots: List[str]
    available_capacity_dose1: str
    available_capacity_dose2: str

    def __post_init__(self):
        # Overriding the available_capacity_dose as available_capacity_dose1 as
        # as we need to show centers for either dose1 or dose2.
        self.available_capacity = self.available_capacity_dose1

    @property
    def slots_str(self):
        return ", ".join(self.slots)

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
        text = f"{self.date}:  {self.vaccine} -> Available Slots\nD1:{self.available_capacity_dose1} | D2: {self.available_capacity_dose2}\n"
        return text


@dataclass()
class VaccineFees:
    vaccine: str
    fee: int


@dataclass(init=False)
class CenterObject:
    center_id: int
    name: str
    address: str
    state_name: str
    district_name: str
    block_name: str
    pincodefee_type: int
    lat: int
    long: int
    _from: str
    to: str
    fee_type: str
    sessions: List[SessionObject]
    vaccine_fees: List[VaccineFees]

    def __init__(self, **kwargs):
        kwargs["_from"] = kwargs["from"]
        del kwargs["from"]
        self._from = kwargs["_from"]

        for a in kwargs:
            setattr(self, a, kwargs[a])
        self.sessions = [SessionObject(**b) for b in kwargs.get("sessions", [])]
        self.vaccine_fees = [VaccineFees(**b) for b in kwargs.get("vaccine_fees", [])]

    @property
    def available_18_sessions(self):
        return [a for a in self.sessions if a.is_18 and a.is_available]

    @property
    def is_18_session_available(self):
        return len(self.available_18_sessions) > 0

    @property
    def min_18_slots_available(self):
        return (
            len(
                [
                    a
                    for a in self.sessions
                    if a.is_18 and a.available_capacity >= MIN_SLOTS
                ]
            )
            > 0
        )

    @property
    def available_45_sessions(self):
        return [a for a in self.sessions if a.is_45 and a.is_available]

    @property
    def min_45_slots_available(self):
        return (
            len(
                [
                    a
                    for a in self.sessions
                    if a.is_45 and a.available_capacity >= MIN_SLOTS
                ]
            )
            > 0
        )

    @property
    def is_45_session_available(self):
        return len(self.available_45_sessions) > 0

    @property
    def detail_available_18_info_str(self):
        text = f"Pin: {self.pincode}"
        if self.fee_type.lower() == FeeType.paid:
            text = text + "<strong>(PAID)</strong> "
        text = text + f"{self.name} {self.address}\n"
        for a in self.available_18_sessions:
            text += a.display_info_str + "\n"
        return text

    @property
    def detail_available_45_info_str(self):
        text = f"Pin: {self.pincode} "
        if self.fee_type.lower() == FeeType.paid:
            text = text + "<strong>(PAID)</strong> "
        text = text + f"{self.name} {self.address}\n"
        for a in self.available_45_sessions:
            text += a.display_info_str + "\n"
        return text
