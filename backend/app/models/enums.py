import enum

class FrequencyType(enum.Enum):
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class DayType(enum.Enum):
    MO = "MO"
    TU = "TU"
    WE = "WE"
    TH = "TH"
    FR = "FR"
    SA = "SA"
    SU = "SU"

class RecurrenceType(enum.Enum):
    ONETIME = "ONETIME"
    RECURRING = "RECURRING"
    EXCEPTION = "EXCEPTION"
