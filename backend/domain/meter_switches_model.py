from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer, String, Table

from core.db import metadata


meter_switches = Table('meter_switches', metadata,
    Column('code', String(64), primary_key=True),
    Column('old_meter', String(160), nullable=False),
    Column('new_meter', String(160), nullable=False),
    Column('handover_hour', Integer, nullable=False),
    Column('approved', Boolean, nullable=False),
    Column('approved_by', String(160), nullable=True),
    Column('approved_at', DateTime, nullable=True),
    # 审签后写入旧表编号；唯一约束保证同一旧表只有先审签的一份换表生效。
    Column('approved_old', String(160), nullable=True, unique=True),
    # 审签后写入新表编号；一块新表只能由一份换表启用一次。
    Column('approved_new', String(160), nullable=True, unique=True),
    CheckConstraint('old_meter <> new_meter'),
    CheckConstraint('handover_hour between 0 and 47'),
)
