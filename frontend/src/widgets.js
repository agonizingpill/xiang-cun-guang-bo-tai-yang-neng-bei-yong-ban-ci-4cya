import {display, el} from './dom.js';

export function status(message, variant = '') {
  return el('p', {class:'status ' + variant, role:'status'}, message);
}

// 每小时表号 [[hour, meter], ...] 或 [{hour, meter}, ...] 压成区间，便于在台账里核对。
function meterRanges(value) {
  const rows = value.map(x => Array.isArray(x) ? [Number(x[0]), x[1]] : [Number(x.hour), x.meter])
    .filter(([hour, meter]) => Number.isFinite(hour) && meter)
    .sort((a, b) => a[0] - b[0]);
  const runs = [];
  for (const [hour, meter] of rows) {
    const last = runs.at(-1);
    if (last && last.meter === meter && hour === last.end + 1) last.end = hour;
    else runs.push({start: hour, end: hour, meter});
  }
  return runs.map(run => `${run.meter} ${run.start}–${run.end} 时`).join('；');
}

export function cell(value) {
  if (Array.isArray(value) && value.length && value.every(x =>
    Array.isArray(x) || (x && typeof x === 'object' && 'hour' in x && 'meter' in x))) {
    return meterRanges(value);
  }
  return display(value);
}

export function dataView(rows, columns, layout) {
  if (!rows.length) return status('暂无可用记录。可先填入一条领域凭证。');
  if (layout === 'table') {
    return el('div', {class:'scroll'}, el('table', {},
      el('thead', {}, el('tr', {}, columns.map(x => el('th', {scope:'col'}, x.label)))),
      el('tbody', {}, rows.map(r => el('tr', {}, columns.map(x => el('td', {}, cell(r[x.name]))))))));
  }
  return el('div', {class:'records ' + layout}, rows.map(row =>
    el('article', {class:'record'}, el('h3',{},display(row[columns[0].name])),
      el('dl',{},columns.slice(1).flatMap(x => [
        el('dt',{},x.label), el('dd',{},cell(row[x.name]))])))));
}
export function titleBlock(kicker, title, detail) {
  return el('header', {class:'title'}, el('span', {class:'kicker'}, kicker), el('h1', {}, title),
    el('p', {class:'intro'}, detail));
}
