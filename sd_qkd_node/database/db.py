"""Manage everything about database."""

from typing import Final

from databases import Database
from orm import ModelRegistry

from sd_qkd_node.configs import Config

local_db: Final[Database] = Database(Config.LOCAL_DB_URL, force_rollback=Config.TESTING)
local_models: Final[ModelRegistry] = ModelRegistry(database=local_db)

shared_db: Final[Database] = Database(
    Config.SHARED_DB_URL, force_rollback=Config.TESTING
)
shared_models: Final[ModelRegistry] = ModelRegistry(database=shared_db)
