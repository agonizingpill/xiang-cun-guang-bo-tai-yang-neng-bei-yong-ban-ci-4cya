from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import meter_switches_service as service
from domain.meter_switches_model import meter_switches
from domain.meter_switches_schemas import ApproveSwitch, SubmitSwitch

router = APIRouter()


@router.get('/meter_switches')
def list_meter_switches(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, meter_switches)


@router.post('/meter_switches/submit-switch')
def submit_switch(data: SubmitSwitch, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.submit_switch(conn, user, data)
        record(conn, user, 'meter_switches.submit_switch')
        return output


@router.post('/meter_switches/approve-switch')
def approve_switch(data: ApproveSwitch, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.approve_switch(conn, user, data)
        record(conn, user, 'meter_switches.approve_switch')
        return output
