from datetime import datetime, timezone

from core.records import get, insert, need, scan, update
from domain.meter_switches_model import meter_switches

HOURS = 48


def _approved(conn):
    return [row for row in scan(conn, meter_switches) if row['approved']]


def switch_by_new(conn, meter):
    return next((row for row in _approved(conn) if row['new_meter'] == meter), None)


def switch_by_old(conn, meter):
    return next((row for row in _approved(conn) if row['old_meter'] == meter), None)


def segments(conn, meter):
    """把两日窗口按交割小时切段，返回升序的 [(start, end, meter), ...]，start 含、end 不含。

    传入的 meter 必须是当前在用的新表号：交割前取旧表，交割小时起取新表。
    """
    superseded = switch_by_old(conn, meter)
    need(superseded is None,
         f'表 {meter} 已在第 {superseded["handover_hour"]} 时交割，请用新表 {superseded["new_meter"]} 核算'
         if superseded else '')
    events = []
    current = meter
    visited = set()
    while True:
        need(current not in visited, '换表链形成回路')
        visited.add(current)
        step = switch_by_new(conn, current)
        if step is None:
            oldest = current
            break
        events.append((step['handover_hour'], current))
        current = step['old_meter']
    result = []
    start, active = 0, oldest
    for hour, incoming in sorted(events):
        need(hour >= start, '换表交割次序冲突')
        if hour > start:
            result.append((start, hour, active))
        start, active = hour, incoming
    if start < HOURS:
        result.append((start, HOURS, active))
    return result


def segments_view(rows):
    return [{'start': start, 'end': end, 'meter': meter} for start, end, meter in rows]


def missing_message(missing):
    parts = [f'{meter} 缺第 ' + '、'.join(str(hour) for hour in hours) + ' 时'
             for meter, hours in missing.items()]
    return '读数未接齐，暂停估算：' + '；'.join(parts)


def submit_switch(conn, user, data):
    need(data.old_meter != data.new_meter, '旧表与新表不能相同')
    need(0 <= data.handover_hour < HOURS, '交割小时须落在两日窗口内')
    return insert(conn, meter_switches, code=data.code, old_meter=data.old_meter,
                  new_meter=data.new_meter, handover_hour=data.handover_hour, approved=False,
                  approved_by=None, approved_at=None, approved_old=None, approved_new=None)


def _reaches(conn, start, target):
    rows = _approved(conn)
    current = start
    visited = set()
    while current not in visited:
        visited.add(current)
        following = next((row for row in rows if row['old_meter'] == current), None)
        if following is None:
            return False
        current = following['new_meter']
        if current == target:
            return True
    return False


def approve_switch(conn, user, data):
    item = get(conn, meter_switches, data.code, lock=True)
    need(not item['approved'], '此换表已审签')
    # 同一旧表只认先审签的一份；读数是否补齐不影响审签。
    winner = switch_by_old(conn, item['old_meter'])
    need(winner is None,
         f'旧表 {item["old_meter"]} 已由 {winner["code"]} 先审签，只认先审签的一份' if winner else '')
    need(switch_by_new(conn, item['new_meter']) is None,
         f'新表 {item["new_meter"]} 已由在先换表启用')
    earlier = switch_by_new(conn, item['old_meter'])
    need(earlier is None or earlier['handover_hour'] < item['handover_hour'], '交割次序与在先换表冲突')
    later = switch_by_old(conn, item['new_meter'])
    need(later is None or later['handover_hour'] > item['handover_hour'], '交割次序与在先换表冲突')
    need(not _reaches(conn, item['new_meter'], item['old_meter']), '换表链形成回路')
    return update(conn, meter_switches, data.code, approved=True, approved_by=user['sub'],
                  approved_at=datetime.now(timezone.utc), approved_old=item['old_meter'],
                  approved_new=item['new_meter'])
