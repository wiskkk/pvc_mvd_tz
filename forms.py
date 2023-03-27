from typing import List
from typing import Optional

from fastapi import Request


class UrlCreateForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.title: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.title = form.get("title")

    def is_valid(self):
        if not self.title or not len(self.title) >= 4:
            self.errors.append("A valid title is required")
        if not self.errors:
            return True
        return False
