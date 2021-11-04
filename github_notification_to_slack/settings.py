from __future__ import annotations

from typing import List

from pydantic import BaseSettings


class AppSettings(BaseSettings):
    event_filters: List[str] = ["published"]

    class Config:
        env_prefix = 'ngx_'


default = AppSettings()
