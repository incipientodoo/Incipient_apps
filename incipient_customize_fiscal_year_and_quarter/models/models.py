# -*- coding: utf-8 -*-
import calendar
import datetime
from datetime import date, datetime as pydt
from dateutil.relativedelta import relativedelta

from odoo import models, api, fields as F
from odoo.fields import Domain


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    # ---------------------------
    # Utilities
    # ---------------------------
    def _fy_start_base(self) -> date:
        """Return fiscal-year *start date* for current year from company settings.
        Company stores the LAST day of FY; start is next day."""
        company = self.env.company
        m = int(company.fiscalyear_last_month or 12)
        d = int(company.fiscalyear_last_day or 31)
        y = date.today().year
        if m == 2:
            if d == 28 and calendar.isleap(y):
                d = 29
            elif d == 29 and not calendar.isleap(y):
                d = 28
        return date(y, m, d) + datetime.timedelta(days=1)

    def _is_datetime_field(self, field_name: str) -> bool:
        fld = self._fields.get(field_name)
        return bool(fld and fld.type == 'datetime')

    def _to_str(self, v, as_datetime: bool) -> str:
        """Coerce date/datetime (or string) to proper Odoo string using the field type."""
        if as_datetime:
            if isinstance(v, date) and not isinstance(v, pydt):
                v = pydt.combine(v, pydt.min.time())
            return v if isinstance(v, str) else F.Datetime.to_string(v)
        else:
            if isinstance(v, pydt):
                v = v.date()
            return v if isinstance(v, str) else F.Date.to_string(v)

    def _min_max_dates(self, domain, field_name):
        """Efficiently get min/max by ordering, without mapping all records."""
        fld = self._fields.get(field_name)
        if not fld or fld.type not in ('date', 'datetime'):
            return (None, None)

        def _edge(order):
            rec = self.search(Domain.AND([domain, [(field_name, '!=', False)]]),
                               order=f"{field_name} {order}", limit=1)
            if not rec:
                return None
            val = rec[field_name]
            return val.date() if isinstance(val, pydt) else val

        mn = _edge('asc')
        mx = _edge('desc')
        return (mn, mx) if (mn and mx) else (None, None)

    def _fy_year_span(self, min_d: date, max_d: date, fy0: date):
        """Return first/last *start-year* that cover [min_d, max_d] for the FY starting at fy0."""
        if not min_d:
            return (None, None)
        start_year = (min_d.year - 1) if min_d < fy0.replace(year=min_d.year) else min_d.year
        end_year   = (max_d.year - 1) if max_d < fy0.replace(year=max_d.year) else max_d.year
        return (start_year, end_year)

    def _iter_buckets(self, domain, field_name, period: str):
        """Yield (start_date, end_date_exclusive) fiscal buckets that may contain data."""
        fy0 = self._fy_start_base()
        min_d, max_d = self._min_max_dates(domain, field_name)
        if not min_d:
            return []  # no data

        start_year, end_year = self._fy_year_span(min_d, max_d, fy0)
        if start_year is None:
            return []

        if period == 'year':
            for y in range(start_year, end_year + 1):
                y_from = fy0.replace(year=y)
                y_to = y_from + relativedelta(years=1)
                yield (y_from, y_to)
        elif period == 'quarter':
            for y in range(start_year, end_year + 1):
                y_from = fy0.replace(year=y)
                for q in range(4):
                    q_from = y_from + relativedelta(months=3*q)
                    q_to   = y_from + relativedelta(months=3*(q+1))
                    yield (q_from, q_to)
        else:
            raise ValueError("Unsupported period")

    def _finalize_time_row(self, row, time_key, start_s, end_s, required_keys):
        """
        Make the row safe for pivot + spreadsheet:
        - ensure every required groupby key exists and is non-empty
        - ensure top-level time key has __range[{time_key}] = {from,to}
        - coerce __count to int
        Return row or None to drop it.
        """
        for g in required_keys:
            if g not in row or row[g] in (None, False, ''):
                return None
        rng = row.get('__range') or {}
        rng[time_key] = {'from': start_s, 'to': end_s}
        row['__range'] = rng
        if '__count' in row and not isinstance(row['__count'], int):
            try:
                row['__count'] = int(row['__count'] or 0)
            except Exception:
                row['__count'] = 0
        return row

    def _fy_label_for_bucket(self, start: date, end_exclusive: date) -> str:
        """Return fiscal-year label by *start* year of the FY containing `start`."""
        fy0 = self._fy_start_base()
        anchor = fy0.replace(year=start.year)
        if start < anchor:
            anchor = anchor.replace(year=anchor.year - 1)
        return f"FY {anchor.year}"

    def _filter_rows_with_data(self, rows, fields):
        """Keep only rows that actually contain data (non-zero __count or any non-zero measure)."""
        kept = []
        for r in rows or []:
            if (r.get('__count') or 0) > 0:
                kept.append(r)
                continue
            for f in (fields or []):
                if f != '__count' and r.get(f):
                    kept.append(r)
                    break
        return kept

    # ---------------------------
    # Fiscal Quarter
    # ---------------------------
    def _fy_quarter_num(self, start_date: date) -> int:
        """Return 1..4 for the fiscal quarter of start_date based on the company's FY start."""
        fy0 = self._fy_start_base()
        anchor = fy0.replace(year=start_date.year)
        if start_date < anchor:
            anchor = anchor.replace(year=anchor.year - 1)
        months = (start_date.year - anchor.year) * 12 + (start_date.month - anchor.month)
        return (months // 3) + 1

    def _read_group_fy_quarter(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        date_field = next((gb.split(':')[0] for gb in groupby if ':quarter' in gb), None)
        if not date_field:
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        if self.env.context.get('disable_fy_grouping'):
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        buckets = self._iter_buckets(domain, date_field, 'quarter')
        if buckets is None:
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        as_dt = self._is_datetime_field(date_field)
        key = f"{date_field}:quarter"

        def _bn(g): return g.split(':')[0]
        same_field = [g for g in groupby if _bn(g) == date_field]
        other_time_on_same_field = any(g != f"{date_field}:quarter" for g in same_field)
        other_fields = any(_bn(g) != date_field for g in groupby)
        has_other = other_time_on_same_field or other_fields

        if has_other:
            non_quarter_gb = [gb for gb in groupby if gb != f"{date_field}:quarter"]
            rows = []
            for start, end in buckets:
                left, right = self._to_str(start, as_dt), self._to_str(end, as_dt)
                q_dom = Domain.AND([domain, [(date_field, '>=', left), (date_field, '<', right)]])

                chunk = super().read_group(q_dom, fields, non_quarter_gb, 0, None, orderby, False)
                chunk = self._filter_rows_with_data(chunk, fields)
                if not chunk:
                    continue

                top_key = f"{date_field}:quarter"
                required = list(non_quarter_gb)
                for r in chunk:
                    qn = self._fy_quarter_num(start)
                    fy_label = self._fy_label_for_bucket(start, end)
                    r[top_key] = f"Q{qn} {fy_label}"
                    r['__domain'] = q_dom
                    r = self._finalize_time_row(r, top_key, left, right, required_keys=required)
                    if r:
                        rows.append(r)

            return rows

        aggregates = [f if ':' in f else f"{f}:sum" for f in fields if f != '__count']

        rows = []
        for start, end in buckets:
            left, right = self._to_str(start, as_dt), self._to_str(end, as_dt)
            q_dom = Domain.AND([domain, [(date_field, '>=', left), (date_field, '<', right)]])
            mlist = super().read_group(q_dom, fields or ['__count'], [], 0, None, orderby, lazy)
            data = mlist[0] if mlist else {}

            if not data or not data.get('__count'):
                continue

            qn = self._fy_quarter_num(start)
            fy_label = self._fy_label_for_bucket(start, end)

            row = {
                key: f"Q{qn} {fy_label}",
                '__domain': q_dom,
                '__count': data.get('__count', 0),
            }

            for agg in aggregates:
                field_name, func = agg.split(":")
                if func == 'sum':
                    val = data.get(field_name)
                    row[field_name] = val if isinstance(val, (int, float)) else (val or 0)

            for f in (fields or []):
                if f != '__count' and f in data:
                    row[f] = data[f]

            row = self._finalize_time_row(row, key, left, right, required_keys=[])
            if row:
                rows.append(row)
        return rows

    # ---------------------------
    # Fiscal Year
    # ---------------------------
    def _read_group_fy_year(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        date_field = next((gb.split(':')[0] for gb in groupby if ':year' in gb), None)
        if not date_field:
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        if self.env.context.get('disable_fy_grouping'):
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        buckets = self._iter_buckets(domain, date_field, 'year')
        if buckets is None:
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        as_dt = self._is_datetime_field(date_field)
        key = f"{date_field}:year"

        def _bn(g): return g.split(':')[0]
        same_field = [g for g in groupby if _bn(g) == date_field]
        other_time_on_same_field = any(g != f"{date_field}:year" for g in same_field)
        other_fields = any(_bn(g) != date_field for g in groupby)
        has_other = other_time_on_same_field or other_fields

        if has_other:
            non_year_gb = [gb for gb in groupby if gb != f"{date_field}:year"]
            rows = []
            quarter_key = f"{date_field}:quarter"

            for start, end in buckets:
                fy_label = self._fy_label_for_bucket(start, end)
                left_y, right_y = self._to_str(start, as_dt), self._to_str(end, as_dt)

                if any(g == quarter_key for g in non_year_gb):
                    other_gb = [g for g in non_year_gb if g != quarter_key]

                    for qi in range(4):
                        q_from = start + relativedelta(months=3 * qi)
                        q_to   = start + relativedelta(months=3 * (qi + 1))
                        left_q, right_q = self._to_str(q_from, as_dt), self._to_str(q_to, as_dt)
                        q_dom = Domain.AND([domain, [
                            (date_field, '>=', left_q),
                            (date_field, '<',  right_q),
                        ]])

                        chunk = super().read_group(q_dom, fields, other_gb, 0, None, orderby, False)
                        chunk = self._filter_rows_with_data(chunk, fields)
                        if not chunk:
                            continue

                        def _has_data(rows):
                            for _r in rows or []:
                                if (_r.get('__count') or 0) > 0:
                                    return True
                                for f in (fields or []):
                                    if f != '__count' and _r.get(f):
                                        return True
                            return False

                        if not _has_data(chunk):
                            continue

                        qn = self._fy_quarter_num(q_from)
                        q_label = f"Q{qn} {fy_label}"

                        for r in chunk:
                            r[f"{date_field}:year"] = fy_label
                            r[quarter_key] = q_label
                            r['__domain'] = q_dom

                            rng = r.get('__range') or {}
                            rng[f"{date_field}:year"] = {'from': left_y,  'to': right_y}
                            rng[quarter_key]          = {'from': left_q,  'to': right_q}
                            r['__range'] = rng

                            rows.append(r)
                else:
                    y_dom = Domain.AND([domain, [
                        (date_field, '>=', left_y),
                        (date_field, '<',  right_y),
                    ]])
                    chunk = super().read_group(y_dom, fields, non_year_gb, 0, None, orderby, False)
                    chunk = self._filter_rows_with_data(chunk, fields)
                    if not chunk:
                        continue

                    for r in chunk:
                        r[f"{date_field}:year"] = fy_label
                        r['__domain'] = y_dom
                        rng = r.get('__range') or {}
                        rng[f"{date_field}:year"] = {'from': left_y, 'to': right_y}
                        r['__range'] = rng
                        rows.append(r)

            return rows

        aggregates = [f if ':' in f else f"{f}:sum" for f in fields if f != '__count']

        rows = []
        for start, end in buckets:
            left, right = self._to_str(start, as_dt), self._to_str(end, as_dt)
            y_dom = Domain.AND([domain, [(date_field, '>=', left), (date_field, '<', right)]])
            mlist = super().read_group(y_dom, fields or ['__count'], [], 0, None, orderby, lazy)
            data = mlist[0] if mlist else {}

            if not data or not data.get('__count'):
                continue

            fy_label = self._fy_label_for_bucket(start, end)
            row = {
                key: fy_label,
                '__domain': y_dom,
                '__count': data.get('__count', 0),
            }

            for agg in aggregates:
                field_name, func = agg.split(":")
                if func == 'sum':
                    val = data.get(field_name)
                    row[field_name] = val if isinstance(val, (int, float)) else (val or 0)

            for f in (fields or []):
                if f != '__count' and f in data:
                    row[f] = data[f]

            row = self._finalize_time_row(row, key, left, right, required_keys=[])
            if row:
                rows.append(row)
        return rows

    # ---------------------------
    # Dispatcher (GLOBAL)
    # ---------------------------
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._name.startswith('documents.document.spreadsheet') or self._name.startswith('spreadsheet.'):
            return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        groupby = [groupby] if isinstance(groupby, str) else list(groupby or [])

        if any(':year' in gb for gb in groupby):
            return self._read_group_fy_year(domain, fields, groupby, offset, limit, orderby, lazy)
        if any(':quarter' in gb for gb in groupby):
            return self._read_group_fy_quarter(domain, fields, groupby, offset, limit, orderby, lazy)

        return super().read_group(domain, fields, groupby, offset, limit, orderby, lazy)
