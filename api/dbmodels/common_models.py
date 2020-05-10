import enum
from gino.ext.aiohttp import Gino
from pydantic import BaseModel
from typing import List, Optional, Tuple, Union
from datetime import datetime


class Privatable(BaseModel):
    def private_dict(self):
        res = self.dict()
        del res['id']
        return res
