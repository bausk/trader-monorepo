from pydantic import BaseModel


class Privatable(BaseModel):
    def private_dict(self):
        res = self.dict()
        if 'id' in res:
            del res['id']
        return res
