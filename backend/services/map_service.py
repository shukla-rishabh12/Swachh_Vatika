"""
Map + hotspot aggregation.
MVP: cluster complaint coordinates by rounding lat/lng to ~500m grid.
"""
from backend.utils.db import get_db, row_to_dict
from collections import defaultdict


# Grid step ~0.005 degrees ≈ 500m at equator
GRID = 0.005


class MapService:

    def get_complaints_map(self, status=None, category=None, limit=500):
        """Return list of complaints with coordinates for map markers."""
        conn = get_db()
        cur = conn.cursor()

        where = ['latitude IS NOT NULL', 'longitude IS NOT NULL']
        params = []
        if status:
            where.append('status = ?')
            params.append(status)
        if category:
            where.append('category = ?')
            params.append(category)

        sql = f'''SELECT id, category, status, priority,
                         latitude, longitude, address, created_at
                  FROM complaints
                  WHERE {' AND '.join(where)}
                  ORDER BY created_at DESC
                  LIMIT ?'''
        rows = cur.execute(sql, params + [limit]).fetchall()
        cur.close()
        return [row_to_dict(r) for r in rows]

    def get_hotspots(self, min_count=2, status=None):
        """
        Group complaints into grid cells. Returns cells with count >= min_count.
        Each cell has a center lat/lng + complaint count.
        """
        conn = get_db()
        cur = conn.cursor()

        where = ['latitude IS NOT NULL', 'longitude IS NOT NULL']
        params = []
        if status:
            where.append('status = ?')
            params.append(status)

        rows = cur.execute(
            f'''SELECT latitude, longitude, category
                FROM complaints
                WHERE {' AND '.join(where)}''',
            params
        ).fetchall()
        cur.close()

        cells = defaultdict(lambda: {'count': 0, 'categories': defaultdict(int)})
        for r in rows:
            lat = r['latitude']
            lng = r['longitude']
            key = (round(lat / GRID) * GRID, round(lng / GRID) * GRID)
            cells[key]['count'] += 1
            cells[key]['categories'][r['category']] += 1

        hotspots = []
        for (lat, lng), data in cells.items():
            if data['count'] < min_count:
                continue
            top_cat = max(data['categories'].items(), key=lambda x: x[1])[0]
            hotspots.append({
                'latitude':  round(lat, 6),
                'longitude': round(lng, 6),
                'count':     data['count'],
                'top_category': top_cat,
                'density':   self._density(data['count']),
            })

        hotspots.sort(key=lambda h: h['count'], reverse=True)
        return hotspots

    def get_ward_hotspots(self):
        """Aggregate complaint count per ward (MVP hotspot view)."""
        cur = get_db().cursor()
        rows = cur.execute(
            '''SELECT w.id AS ward_id, w.name AS ward_name, w.code AS ward_code,
                      COUNT(c.id) AS count
               FROM wards w
               LEFT JOIN complaints c ON c.ward_id = w.id
               GROUP BY w.id, w.name, w.code
               ORDER BY count DESC'''
        ).fetchall()
        cur.close()

        data = [row_to_dict(r) for r in rows]
        max_count = max([d['count'] for d in data], default=0)
        for d in data:
            d['density'] = self._density(d['count'], max_count)
        return data

    @staticmethod
    def _density(count, max_count=None):
        """Bucket count into LOW/MEDIUM/HIGH."""
        if max_count:
            if max_count == 0:
                return 'LOW'
            ratio = count / max_count
            if ratio >= 0.66:
                return 'HIGH'
            if ratio >= 0.33:
                return 'MEDIUM'
            return 'LOW'
        # Simple absolute thresholds for grids
        if count >= 5:
            return 'HIGH'
        if count >= 3:
            return 'MEDIUM'
        return 'LOW'