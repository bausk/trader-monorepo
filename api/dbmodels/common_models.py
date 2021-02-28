from pydantic import BaseModel


class Privatable(BaseModel):
    def private_dict(self, without=None):
        if without is None:
            without = ["id"]
        else:
            without += ["id"]
        res = self.dict(exclude_none=True)
        for excluded in without:
            if excluded in res:
                del res[excluded]
        return res
