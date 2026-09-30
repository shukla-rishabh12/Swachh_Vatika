"""
MEGA SEED — Swachh-Seva
Creates: 55 users, 100+ complaints, 40 pickups, 35 tasks,
token transactions, notifications (citizens + workers + admins), audit logs.
Run: python database/seed.py
"""
import os
import sys
import random
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flask import Flask
from config import get_config
from backend.utils.db import init_db, get_db
from backend.utils.auth import hash_password


# Deterministic randomness for reproducible demo
random.seed(42)


def utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def days_ago(n, hours=0):
    dt = datetime.now(timezone.utc) - timedelta(days=n, hours=hours)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


# =========================================================
# WARDS
# =========================================================
WARDS = [
    ('Ward 01 - Civil Lines',   'W01', 'Central zone'),
    ('Ward 02 - Kidwai Nagar',  'W02', 'North zone'),
    ('Ward 03 - Swaroop Nagar', 'W03', 'South zone'),
    ('Ward 04 - Arya Nagar',    'W04', 'East zone'),
    ('Ward 05 - Govind Nagar',  'W05', 'West zone'),
    ('Ward 06 - Kakadeo',       'W06', 'Central-south zone'),
]

# =========================================================
# SETTINGS
# =========================================================
SETTINGS = [
    ('REPORT_REWARD',           '5',    'Tokens awarded for verified waste report'),
    ('PICKUP_REWARD',           '3',    'Tokens awarded for completed pickup'),
    ('MAX_IMAGE_SIZE_MB',       '5',    'Maximum upload size in MB'),
    ('DUPLICATE_WINDOW_HOURS',  '24',   'Window for duplicate complaint detection'),
    ('MAX_CHAT_MESSAGE_LENGTH', '1000', 'Max AI chat message length'),
]

# =========================================================
# USERS
# =========================================================
FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan',
    'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advik', 'Pranav', 'Aryan',
    'Diya', 'Aadhya', 'Saanvi', 'Ananya', 'Ishita', 'Kiara', 'Myra', 'Sara',
    'Riya', 'Anika', 'Navya', 'Pari', 'Anvi', 'Prisha', 'Meera',
    'Rohan', 'Karan', 'Nikhil', 'Rahul', 'Amit', 'Suresh', 'Vijay', 'Raj',
    'Neha', 'Priya', 'Pooja', 'Kavita', 'Sunita', 'Rekha', 'Anita',
    'Rishabh', 'Mohit', 'Sahil', 'Tarun', 'Manish',
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Yadav', 'Mishra', 'Tiwari',
    'Pandey', 'Chauhan', 'Agarwal', 'Jain', 'Saxena', 'Srivastava', 'Rastogi',
    'Khan', 'Ansari', 'Sheikh', 'Kapoor', 'Malhotra',
]

CITIES = ['Kanpur', 'Lucknow', 'Noida', 'Varanasi']

COMPLAINT_CATEGORIES = [
    'GARBAGE_DUMP', 'OVERFLOWING_BIN', 'PLASTIC_WASTE',
    'CONSTRUCTION_WASTE', 'DRAIN_WASTE', 'OPEN_DUMPING',
    'DEAD_ANIMAL', 'OTHER',
]

COMPLAINT_DESCRIPTIONS = {
    'GARBAGE_DUMP': [
        'Garbage has been piling up near the main market for 3 days.',
        'Large pile of waste near community center, causing bad smell.',
        'Trash accumulated behind the bus stop for over a week.',
        'Waste dumped on empty plot next to residential area.',
    ],
    'OVERFLOWING_BIN': [
        'Public dustbin near the park is overflowing since yesterday.',
        'Bin near the school gate has not been cleared in days.',
        'Community bin is full and waste is spilling on road.',
        'Municipal bin at the corner is completely overflowing.',
    ],
    'PLASTIC_WASTE': [
        'Plastic bottles and bags dumped near the river bank.',
        'Large quantity of plastic waste blocking the footpath.',
        'Plastic wrappers and bottles scattered on the roadside.',
        'Illegal plastic dumping near the canal area.',
    ],
    'CONSTRUCTION_WASTE': [
        'Construction debris left on the road since last week.',
        'Bricks and cement waste blocking the street.',
        'Construction material dumped on public land.',
        'Debris from nearby site not cleared for many days.',
    ],
    'DRAIN_WASTE': [
        'Drain near school is choked with waste and stagnant water.',
        'Open drain full of garbage, mosquitoes breeding.',
        'Drain blocked with plastic, water overflowing on street.',
        'Sewage drain choked with garbage for over a week.',
    ],
    'OPEN_DUMPING': [
        'People are openly dumping waste on the roadside.',
        'Regular illegal dumping happening on the empty lot.',
        'Waste being dumped near the temple premises.',
        'Open dumping near playground, unsafe for children.',
    ],
    'DEAD_ANIMAL': [
        'Dead dog lying on the roadside since morning.',
        'Dead animal near the park, urgent cleanup needed.',
        'Carcass on the road, causing health hazard.',
    ],
    'OTHER': [
        'Mixed waste causing problem in the area.',
        'Unusual waste accumulation needs attention.',
        'Multiple waste issues in the neighborhood.',
    ],
}

PICKUP_WASTE_TYPES = [
    'HOUSEHOLD_WASTE', 'BULKY_WASTE', 'E_WASTE',
    'GARDEN_WASTE', 'CONSTRUCTION_DEBRIS', 'OTHER',
]

PICKUP_DESCRIPTIONS = [
    'Mixed household waste, approx 5 kg.',
    'Old furniture and bulky items for pickup.',
    'E-waste including old phone and charger.',
    'Garden waste from pruning, 3 bags.',
    'Construction debris from small renovation.',
    'General waste pickup request.',
]


def make_users():
    """Generate 55 users: 40 citizens, 10 workers, 5 admins."""
    users = []

    # 3 demo users (simple passwords)
    users.append(('citizen@example.com', 'citizen123', 'CITIZEN', 'Demo Citizen',  '9876543210'))
    users.append(('worker@example.com',  'worker123',  'WORKER',  'Demo Worker',   '9876543211'))
    users.append(('admin@example.com',   'admin123',   'ADMIN',   'Demo Admin',    '9876543212'))

    # 4 more admins
    for i in range(4):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        users.append((
            f'admin{i+1}@swachh.in', 'password123', 'ADMIN',
            f'{fn} {ln}', f'900000000{i}'
        ))

    # 9 more workers
    for i in range(9):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        users.append((
            f'worker{i+1}@swachh.in', 'password123', 'WORKER',
            f'{fn} {ln}', f'910000000{i}'
        ))

    # 39 more citizens
    used_emails = {u[0] for u in users}
    for i in range(39):
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        email = f'citizen{i+1}@swachh.in'
        while email in used_emails:
            email = f'citizen{i+100}@swachh.in'
        used_emails.add(email)
        users.append((
            email, 'password123', 'CITIZEN',
            f'{fn} {ln}', f'98000{i:05d}'[:10]
        ))

    return users


# =========================================================
# MAIN SEED
# =========================================================
def run():
    app = Flask(__name__)
    app.config.from_object(get_config())

    db_path = app.config['DATABASE_PATH']
    print(f'\n[SEED] Seeding database: {db_path}')
    init_db(db_path)

    with app.app_context():
        conn = get_db()
        cur = conn.cursor()

        # ---------- WARDS ----------
        for name, code, desc in WARDS:
            cur.execute(
                '''INSERT OR IGNORE INTO wards
                   (name, code, description, is_active, created_at)
                   VALUES (?, ?, ?, 1, ?)''',
                (name, code, desc, utc_now())
            )
        conn.commit()

        # ---------- SETTINGS ----------
        for key, value, desc in SETTINGS:
            cur.execute(
                '''INSERT OR IGNORE INTO system_settings
                   (setting_key, setting_value, description, updated_at)
                   VALUES (?, ?, ?, ?)''',
                (key, value, desc, utc_now())
            )
        conn.commit()

        # ---------- USERS ----------
        all_users = make_users()
        user_ids = {'CITIZEN': [], 'WORKER': [], 'ADMIN': []}

        print(f'\n[USERS] Creating {len(all_users)} users...')
        for email, password, role, full_name, phone in all_users:
            row = cur.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
            if row:
                user_ids[role].append(row[0])
                continue

            now = utc_now()
            cur.execute(
                '''INSERT INTO users
                   (email, password_hash, role, is_active, created_at, updated_at)
                   VALUES (?, ?, ?, 1, ?, ?)''',
                (email, hash_password(password), role, now, now)
            )
            uid = cur.lastrowid
            user_ids[role].append(uid)

            ward_id = random.randint(1, len(WARDS))
            address = f'{random.randint(1, 200)} {random.choice(["MG Road", "Park Street", "Church Lane", "Nehru Nagar", "Gandhi Marg"])}'
            city = random.choice(CITIES)
            cur.execute(
                '''INSERT INTO profiles
                   (user_id, full_name, phone, address, city, ward_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (uid, full_name, phone, address, city, ward_id, now, now)
            )

            cur.execute(
                '''INSERT INTO token_wallets
                   (user_id, balance, lifetime_earned, lifetime_spent, updated_at)
                   VALUES (?, 0, 0, 0, ?)''',
                (uid, now)
            )
            conn.commit()

        conn.commit()
        print(f'   [OK] {len(user_ids["CITIZEN"])} citizens, {len(user_ids["WORKER"])} workers, {len(user_ids["ADMIN"])} admins')

        # ---------- COMPLAINTS ----------
        print('\n[COMPLAINTS] Creating complaints...')
        existing = cur.execute('SELECT COUNT(*) FROM complaints').fetchone()[0]

        status_plan = [
            ('SUBMITTED',         15),
            ('UNDER_REVIEW',      10),
            ('VERIFIED',           8),
            ('REJECTED',           6),
            ('ASSIGNED',           8),
            ('IN_PROGRESS',        8),
            ('WORKER_COMPLETED',   8),
            ('ADMIN_VERIFIED',     6),
            ('CLOSED',            25),
            ('CANCELLED',          3),
        ]

        complaint_ids_by_status = {k: [] for k, _ in status_plan}
        all_complaint_ids = []

        if existing == 0:
            for status, count in status_plan:
                for _ in range(count):
                    citizen_id = random.choice(user_ids['CITIZEN'])
                    category = random.choice(COMPLAINT_CATEGORIES)
                    desc = random.choice(COMPLAINT_DESCRIPTIONS[category])
                    lat = 26.4 + random.uniform(-0.1, 0.1)
                    lng = 80.3 + random.uniform(-0.1, 0.1)
                    ward_id = random.randint(1, len(WARDS))
                    priority = random.choices(
                        ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                        weights=[20, 40, 30, 10]
                    )[0]
                    created = days_ago(random.randint(1, 60))

                    cur.execute(
                        '''INSERT INTO complaints
                           (citizen_id, category, description, latitude, longitude,
                            address, ward_id, priority, status, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (citizen_id, category, desc, lat, lng,
                         f'{random.randint(1,200)} {random.choice(["MG Road","Park Street","Nehru Nagar"])}',
                         ward_id, priority, status, created, created)
                    )
                    cid = cur.lastrowid
                    all_complaint_ids.append(cid)
                    complaint_ids_by_status[status].append(cid)

                    flow = ['SUBMITTED', 'UNDER_REVIEW', 'VERIFIED', 'ASSIGNED',
                            'IN_PROGRESS', 'WORKER_COMPLETED', 'ADMIN_VERIFIED', 'CLOSED']
                    if status == 'REJECTED':
                        steps = ['SUBMITTED', 'UNDER_REVIEW', 'REJECTED']
                    elif status == 'CANCELLED':
                        steps = ['SUBMITTED', 'CANCELLED']
                    else:
                        try:
                            idx = flow.index(status)
                            steps = flow[:idx+1]
                        except ValueError:
                            steps = ['SUBMITTED']

                    prev = None
                    for st in steps:
                        actor = citizen_id if st == 'SUBMITTED' else random.choice(user_ids['ADMIN'])
                        cur.execute(
                            '''INSERT INTO complaint_status_history
                               (complaint_id, old_status, new_status, changed_by, reason, created_at)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                            (cid, prev, st, actor, None, created)
                        )
                        prev = st

                    if status in ('ADMIN_VERIFIED', 'CLOSED'):
                        cur.execute(
                            'UPDATE complaints SET verified_at = ?, closed_at = ? WHERE id = ?',
                            (created, created, cid)
                        )

            conn.commit()
            print(f'   [OK] {len(all_complaint_ids)} complaints created')
        else:
            print(f'   [SKIP] Complaints already exist ({existing})')
            all_complaint_ids = [r[0] for r in cur.execute('SELECT id FROM complaints').fetchall()]

        # ---------- PICKUPS ----------
        print('\n[PICKUPS] Creating pickups...')
        existing_pickups = cur.execute('SELECT COUNT(*) FROM pickup_requests').fetchone()[0]
        pickup_ids = []
        if existing_pickups == 0:
            pickup_statuses = (['SUBMITTED']*10 + ['UNDER_REVIEW']*6 + ['APPROVED']*4 +
                               ['ASSIGNED']*5 + ['COMPLETED']*12 + ['REJECTED']*2 + ['CANCELLED']*1)
            random.shuffle(pickup_statuses)

            for i in range(40):
                citizen_id = random.choice(user_ids['CITIZEN'])
                status = pickup_statuses[i]
                waste_type = random.choice(PICKUP_WASTE_TYPES)
                desc = random.choice(PICKUP_DESCRIPTIONS)
                lat = 26.4 + random.uniform(-0.1, 0.1)
                lng = 80.3 + random.uniform(-0.1, 0.1)
                preferred = (datetime.now() + timedelta(days=random.randint(1, 10))).strftime('%Y-%m-%d')
                created = days_ago(random.randint(1, 45))

                cur.execute(
                    '''INSERT INTO pickup_requests
                       (citizen_id, waste_type, description, latitude, longitude,
                        address, preferred_date, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (citizen_id, waste_type, desc, lat, lng,
                     f'{random.randint(1,200)} Street', preferred, status, created, created)
                )
                pickup_ids.append(cur.lastrowid)
            conn.commit()
            print(f'   [OK] {len(pickup_ids)} pickups created')
        else:
            print(f'   [SKIP] Pickups already exist ({existing_pickups})')
            pickup_ids = [r[0] for r in cur.execute('SELECT id FROM pickup_requests').fetchall()]

        # ---------- TASKS ----------
        print('\n[TASKS] Creating tasks...')
        existing_tasks = cur.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        task_ids = []
        if existing_tasks == 0:
            assignable_statuses = ['ASSIGNED', 'IN_PROGRESS', 'WORKER_COMPLETED',
                                   'ADMIN_VERIFIED', 'CLOSED']
            assignable = []
            for st in assignable_statuses:
                rows = cur.execute(
                    'SELECT id, status, citizen_id FROM complaints WHERE status = ?',
                    (st,)
                ).fetchall()
                for r in rows:
                    assignable.append({'id': r[0], 'status': r[1], 'citizen_id': r[2]})

            for c in assignable:
                worker_id = random.choice(user_ids['WORKER'])
                admin_id  = random.choice(user_ids['ADMIN'])
                cstatus = c['status']

                if cstatus == 'ASSIGNED':
                    task_status = random.choice(['ASSIGNED', 'ACCEPTED'])
                elif cstatus == 'IN_PROGRESS':
                    task_status = 'IN_PROGRESS'
                elif cstatus == 'WORKER_COMPLETED':
                    task_status = 'COMPLETED'
                elif cstatus in ('ADMIN_VERIFIED', 'CLOSED'):
                    task_status = random.choice(['VERIFIED', 'VERIFICATION_FAILED'])
                else:
                    task_status = 'ASSIGNED'

                assigned_at = days_ago(random.randint(3, 30))
                cur.execute(
                    '''INSERT INTO tasks
                       (complaint_id, worker_id, assigned_by, status,
                        assigned_at, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (c['id'], worker_id, admin_id, task_status,
                     assigned_at, assigned_at, assigned_at)
                )
                tid = cur.lastrowid
                task_ids.append(tid)

                if task_status in ('ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'VERIFICATION_FAILED'):
                    cur.execute('UPDATE tasks SET accepted_at = ? WHERE id = ?',
                                (days_ago(random.randint(2, 20)), tid))
                if task_status in ('IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'VERIFICATION_FAILED'):
                    cur.execute('UPDATE tasks SET started_at = ? WHERE id = ?',
                                (days_ago(random.randint(1, 15)), tid))
                if task_status in ('COMPLETED', 'VERIFIED', 'VERIFICATION_FAILED'):
                    cur.execute('UPDATE tasks SET completed_at = ? WHERE id = ?',
                                (days_ago(random.randint(1, 10)), tid))
                if task_status == 'VERIFIED':
                    cur.execute('UPDATE tasks SET verified_at = ? WHERE id = ?',
                                (days_ago(random.randint(0, 5)), tid))

            conn.commit()
            print(f'   [OK] {len(task_ids)} tasks created')
        else:
            print(f'   [SKIP] Tasks already exist ({existing_tasks})')
            task_ids = [r[0] for r in cur.execute('SELECT id FROM tasks').fetchall()]

        # ---------- TOKEN TRANSACTIONS ----------
        print('\n[TOKENS] Creating token transactions...')
        existing_tx = cur.execute('SELECT COUNT(*) FROM token_transactions').fetchone()[0]
        if existing_tx == 0:
            closed = cur.execute(
                '''SELECT id, citizen_id FROM complaints
                   WHERE status IN ('CLOSED', 'ADMIN_VERIFIED')'''
            ).fetchall()

            tx_count = 0
            for cid, citizen_id in closed:
                wallet = cur.execute(
                    'SELECT id FROM token_wallets WHERE user_id = ?', (citizen_id,)
                ).fetchone()
                if not wallet:
                    continue
                amount = 5
                created = days_ago(random.randint(0, 30))
                cur.execute(
                    '''INSERT INTO token_transactions
                       (wallet_id, user_id, transaction_type, amount,
                        source_type, source_id, description, created_at)
                       VALUES (?, ?, 'EARN', ?, 'COMPLAINT', ?, ?, ?)''',
                    (wallet[0], citizen_id, amount, cid,
                     f'Complaint #{cid} closed', created)
                )
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance + ?,
                           lifetime_earned = lifetime_earned + ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, amount, created, wallet[0])
                )
                tx_count += 1

            completed_pickups = cur.execute(
                "SELECT id, citizen_id FROM pickup_requests WHERE status = 'COMPLETED'"
            ).fetchall()
            for pid, citizen_id in completed_pickups:
                wallet = cur.execute(
                    'SELECT id FROM token_wallets WHERE user_id = ?', (citizen_id,)
                ).fetchone()
                if not wallet:
                    continue
                amount = 3
                created = days_ago(random.randint(0, 30))
                cur.execute(
                    '''INSERT INTO token_transactions
                       (wallet_id, user_id, transaction_type, amount,
                        source_type, source_id, description, created_at)
                       VALUES (?, ?, 'EARN', ?, 'PICKUP', ?, ?, ?)''',
                    (wallet[0], citizen_id, amount, pid,
                     f'Pickup #{pid} completed', created)
                )
                cur.execute(
                    '''UPDATE token_wallets
                       SET balance = balance + ?,
                           lifetime_earned = lifetime_earned + ?,
                           updated_at = ?
                       WHERE id = ?''',
                    (amount, amount, created, wallet[0])
                )
                tx_count += 1

            for _ in range(5):
                user_id = random.choice(user_ids['CITIZEN'])
                wallet = cur.execute(
                    'SELECT id FROM token_wallets WHERE user_id = ?', (user_id,)
                ).fetchone()
                if not wallet:
                    continue
                amount = random.choice([10, 15, -5, 20])
                created = days_ago(random.randint(0, 15))
                cur.execute(
                    '''INSERT INTO token_transactions
                       (wallet_id, user_id, transaction_type, amount,
                        source_type, source_id, description, created_at)
                       VALUES (?, ?, 'ADJUSTMENT', ?, 'ADMIN_ADJUSTMENT', NULL, ?, ?)''',
                    (wallet[0], user_id, amount,
                     'Manual admin adjustment', created)
                )
                if amount >= 0:
                    cur.execute(
                        '''UPDATE token_wallets
                           SET balance = balance + ?, updated_at = ?
                           WHERE id = ?''',
                        (amount, created, wallet[0])
                    )
                else:
                    cur.execute(
                        '''UPDATE token_wallets
                           SET balance = balance + ?, lifetime_spent = lifetime_spent + ?
                           WHERE id = ?''',
                        (amount, abs(amount), wallet[0])
                    )
                tx_count += 1

            conn.commit()
            print(f'   [OK] {tx_count} transactions created')
        else:
            print(f'   [SKIP] Transactions already exist ({existing_tx})')

        # ---------- NOTIFICATIONS ----------
        print('\n[NOTIFICATIONS] Creating notifications...')
        existing_notifs = cur.execute('SELECT COUNT(*) FROM notifications').fetchone()[0]
        if existing_notifs == 0:
            notif_count = 0

            # ---- Citizen notifications ----
            sample = cur.execute(
                'SELECT id, citizen_id, status FROM complaints ORDER BY RANDOM() LIMIT 60'
            ).fetchall()
            for cid, citizen_id, status in sample:
                title = 'Complaint update'
                msg = f'Your complaint #{cid} status: {status.replace("_", " ")}.'
                created = days_ago(random.randint(0, 20))
                is_read = random.choice([0, 1])
                cur.execute(
                    '''INSERT INTO notifications
                       (user_id, type, title, message, related_entity_type, related_entity_id, is_read, created_at)
                       VALUES (?, 'COMPLAINT_UPDATE', ?, ?, 'COMPLAINT', ?, ?, ?)''',
                    (citizen_id, title, msg, cid, is_read, created)
                )
                notif_count += 1

            # ---- Worker notifications ----
            worker_notifs = cur.execute(
                'SELECT id, worker_id FROM tasks ORDER BY RANDOM() LIMIT 30'
            ).fetchall()
            for tid, worker_id in worker_notifs:
                created = days_ago(random.randint(0, 20))
                is_read = random.choice([0, 1])
                cur.execute(
                    '''INSERT INTO notifications
                       (user_id, type, title, message, related_entity_type, related_entity_id, is_read, created_at)
                       VALUES (?, 'WORKER_ASSIGNED', ?, ?, 'TASK', ?, ?, ?)''',
                    (worker_id, 'New task assigned',
                     f'Task #{tid} has been assigned to you.',
                     tid, is_read, created)
                )
                notif_count += 1

            # ---- Admin notifications: complaints awaiting review ----
            admin_sample = cur.execute(
                'SELECT id, category, status FROM complaints ORDER BY RANDOM() LIMIT 25'
            ).fetchall()
            for cid, cat, stat in admin_sample:
                for admin_id in user_ids['ADMIN']:
                    created = days_ago(random.randint(0, 15))
                    is_read = random.choice([0, 0, 1])  # ~66% unread
                    cur.execute(
                        '''INSERT INTO notifications
                           (user_id, type, title, message,
                            related_entity_type, related_entity_id, is_read, created_at)
                           VALUES (?, 'ADMIN_ALERT', ?, ?, 'COMPLAINT', ?, ?, ?)''',
                        (admin_id,
                         'New complaint needs review',
                         f'Complaint #{cid} ({cat}) status: {stat}.',
                         cid, is_read, created)
                    )
                    notif_count += 1

            # ---- Admin notifications: tasks awaiting verification ----
            task_sample = cur.execute(
                "SELECT id FROM tasks WHERE status IN ('COMPLETED','VERIFICATION_FAILED') LIMIT 15"
            ).fetchall()
            for (tid,) in task_sample:
                for admin_id in user_ids['ADMIN']:
                    created = days_ago(random.randint(0, 10))
                    is_read = random.choice([0, 1])
                    cur.execute(
                        '''INSERT INTO notifications
                           (user_id, type, title, message,
                            related_entity_type, related_entity_id, is_read, created_at)
                           VALUES (?, 'ADMIN_ALERT', ?, ?, 'TASK', ?, ?, ?)''',
                        (admin_id,
                         'Task awaiting verification',
                         f'Task #{tid} needs your review.',
                         tid, is_read, created)
                    )
                    notif_count += 1

            conn.commit()
            print(f'   [OK] {notif_count} notifications created')
        else:
            print(f'   [SKIP] Notifications already exist ({existing_notifs})')

        # ---------- AUDIT LOGS ----------
        print('\n[AUDIT] Creating audit logs...')
        existing_logs = cur.execute('SELECT COUNT(*) FROM audit_logs').fetchone()[0]
        if existing_logs == 0:
            log_count = 0

            verified = cur.execute(
                "SELECT id FROM complaints WHERE status IN ('VERIFIED','CLOSED','ADMIN_VERIFIED') LIMIT 30"
            ).fetchall()
            for (cid,) in verified:
                admin_id = random.choice(user_ids['ADMIN'])
                created = days_ago(random.randint(0, 30))
                cur.execute(
                    '''INSERT INTO audit_logs
                       (actor_user_id, action, entity_type, entity_id,
                        old_value, new_value, ip_address, created_at)
                       VALUES (?, 'ADMIN_VERIFIED_COMPLAINT', 'COMPLAINT', ?, ?, ?, ?, ?)''',
                    (admin_id, cid, 'UNDER_REVIEW', 'VERIFIED',
                     f'192.168.1.{random.randint(2,200)}', created)
                )
                log_count += 1

            assigned = cur.execute(
                'SELECT id, worker_id FROM tasks LIMIT 30'
            ).fetchall()
            for tid, wid in assigned:
                admin_id = random.choice(user_ids['ADMIN'])
                created = days_ago(random.randint(0, 30))
                cur.execute(
                    '''INSERT INTO audit_logs
                       (actor_user_id, action, entity_type, entity_id,
                        new_value, ip_address, created_at)
                       VALUES (?, 'WORKER_ASSIGNED', 'TASK', ?, ?, ?, ?)''',
                    (admin_id, tid,
                     f'{{"worker_id": {wid}}}',
                     f'192.168.1.{random.randint(2,200)}', created)
                )
                log_count += 1

            task_verified = cur.execute(
                "SELECT id FROM tasks WHERE status IN ('VERIFIED','VERIFICATION_FAILED') LIMIT 20"
            ).fetchall()
            for (tid,) in task_verified:
                admin_id = random.choice(user_ids['ADMIN'])
                created = days_ago(random.randint(0, 20))
                cur.execute(
                    '''INSERT INTO audit_logs
                       (actor_user_id, action, entity_type, entity_id,
                        new_value, ip_address, created_at)
                       VALUES (?, 'ADMIN_VERIFIED_TASK', 'TASK', ?, ?, ?, ?)''',
                    (admin_id, tid, '{"approved": true}',
                     f'192.168.1.{random.randint(2,200)}', created)
                )
                log_count += 1

            conn.commit()
            print(f'   [OK] {log_count} audit logs created')
        else:
            print(f'   [SKIP] Audit logs already exist ({existing_logs})')

        cur.close()

    # ---------- FINAL REPORT ----------
    print('\n' + '='*60)
    print('[DONE] SEED COMPLETE - Summary')
    print('='*60)
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        for label, table in [
            ('Users',            'users'),
            ('Complaints',       'complaints'),
            ('Pickups',          'pickup_requests'),
            ('Tasks',            'tasks'),
            ('Token tx',         'token_transactions'),
            ('Notifications',    'notifications'),
            ('Audit logs',       'audit_logs'),
            ('Wards',            'wards'),
            ('Status history',   'complaint_status_history'),
        ]:
            n = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
            print(f'  {label:20s}: {n}')
        cur.close()

    print('\n' + '='*60)
    print('KEY DEMO LOGIN CREDENTIALS')
    print('='*60)
    print('  CITIZEN  | citizen@example.com      | citizen123')
    print('  WORKER   | worker@example.com       | worker123')
    print('  ADMIN    | admin@example.com        | admin123')
    print()
    print('  Bulk users (all password123):')
    print('    citizens: citizen1@swachh.in ... citizen39@swachh.in')
    print('    workers:  worker1@swachh.in  ... worker9@swachh.in')
    print('    admins:   admin1@swachh.in   ... admin4@swachh.in')
    print()


if __name__ == '__main__':
    run()