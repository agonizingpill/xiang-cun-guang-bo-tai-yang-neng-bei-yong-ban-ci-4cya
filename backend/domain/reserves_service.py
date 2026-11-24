from core.queueing import submit, result
from core.records import get, insert, need, scan
from domain import meter_switches_service as switches
from domain.airslots_model import airslots
from domain.battery_logs_model import battery_logs
from domain.reserves_model import reserves

HOURS = switches.HOURS
MIN_HOURS = 36


def _expected(segments):
    return {hour: meter for start, end, meter in segments for hour in range(start, end)}


def _contiguous(rows):
    return len(rows) >= MIN_HOURS and all(y['hour'] - x['hour'] == 1 for x, y in zip(rows, rows[1:]))


def _missing_message(expected, missing):
    grouped = {}
    for hour in sorted(missing):
        grouped.setdefault(expected[hour], []).append(hour)
    return switches.missing_message(grouped)


def forecast_wh(conn, user, data):
    slot = get(conn, airslots, data.airslot)
    segments = switches.segments(conn, data.meter)
    expected = _expected(segments)
    records = {(row['meter'], row['hour']): row for row in scan(conn, battery_logs) if row['verified']}
    if len(segments) > 1:
        # 换表日：两日窗口跨新旧两块表。晚到读数只要经审签就落回它所属那段；
        # 缺小时则暂停，并点名缺哪块表、几点。接齐后按原规则回测和预测。
        rows = sorted((records[(expected[hour], hour)] for hour in expected
                       if (expected[hour], hour) in records), key=lambda row: row['hour'])
        missing = [hour for hour in expected if (expected[hour], hour) not in records]
        need(not missing, _missing_message(expected, missing))
        need(_contiguous(rows), '要有连续三十六小时审签读数')
    else:
        rows = sorted([row for row in scan(conn, battery_logs)
                       if row['meter'] == data.meter and row['verified']], key=lambda row: row['hour'])
        need(_contiguous(rows), '要有连续三十六小时审签读数')
    hour_map = [{'hour': row['hour'], 'meter': expected[row['hour']]} for row in rows]
    return submit(user, {'window': slot, 'rows': rows, 'clear': data.clear, 'meter': data.meter,
                         'segments': switches.segments_view(segments), 'hour_map': hour_map})


def save_reserve(conn, user, data):
    run = result(user, data.token)
    window = run['input']['window']
    stats = run['result']
    need(get(conn, airslots, window['code'])['hour'] == window['hour'], '节目时间已变')
    return insert(conn, reserves, code=data.code, airslot=window['code'], plan_wh=stats['plan_wh'],
                  fallback='本地优先' if window['offline'] else '受控中继', mae=stats['mae'],
                  token=data.token, meter=run['input'].get('meter'),
                  meters=stats.get('hour_map') or run['input'].get('hour_map'))
