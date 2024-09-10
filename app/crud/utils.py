from datetime import datetime
from typing import Union

from app.models import CharityProject, Donation


async def close_entry(entry: Union[CharityProject, Donation]
                      ) -> Union[CharityProject, Donation]:
    entry.invested_amount = entry.full_amount
    entry.fully_invested = True
    entry.close_date = datetime.now()
    return entry
