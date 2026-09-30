================================================================
  SWACHH_VATIKA — Citizen-Centric Municipal Waste Management
================================================================

A citizen-centric municipal waste management platform connecting
citizens, field workers, and municipal administrators to report,
track, and resolve waste-related issues — with AI assistance and
token-based incentives.


================================================================
  ABOUT THE PROJECT
================================================================

Swachh_Vatika digitizes the entire lifecycle of municipal waste
management. It bridges the gap between three key stakeholders:

  - Citizens    who report waste problems in their neighborhood
  - Field Workers   who physically resolve those problems
  - Admins      who verify, assign, and monitor the operation

Every action is tracked, verified, and rewarded with
"SwachhTokens" — an internal points system that encourages
civic participation.

The platform includes an AI Civic Assistant powered by Groq to
help citizens and admins with natural-language queries about
complaints, pickups, and platform usage.


================================================================
  DEMO ACCOUNTS (Ready to Use)
================================================================

  CITIZEN  |  citizen@example.com  |  citizen123
  WORKER   |  worker@example.com   |  worker123
  ADMIN    |  admin@example.com    |  admin123

The seed script also creates:
  - 55 users total (40 citizens, 10 workers, 5 admins)
  - ~100 complaints across all statuses
  - 40 pickup requests
  - 35 tasks
  - Token transactions, notifications, and audit logs

Bulk users (all password: password123):
  - citizen1@swachh.in  ... citizen39@swachh.in
  - worker1@swachh.in   ... worker9@swachh.in
  - admin1@swachh.in    ... admin4@swachh.in


================================================================
  TECH STACK
================================================================

  Frontend    :  HTML5 + CSS3 + Vanilla JavaScript
  Backend     :  Python 3.x + Flask + Flask-CORS
  Database    :  SQLite (via Python sqlite3)
  AI          :  Groq API (server-side only)
  Auth        :  Flask sessions + Werkzeug password hashing
  Deployment  :  Render (via Gunicorn)

NO React. NO Node.js. NO external CSS frameworks.
Everything is intentionally lightweight and framework-free.


================================================================
  FEATURES
================================================================

CITIZEN MODULE
  - Register, login, manage profile
  - Report waste with photo, category, description, GPS location
  - Request pickup (household / bulky / e-waste / garden)
  - Track complaints across every status:
      SUBMITTED > UNDER_REVIEW > VERIFIED > ASSIGNED >
      IN_PROGRESS > WORKER_COMPLETED > ADMIN_VERIFIED > CLOSED
  - SwachhToken wallet — earn tokens for verified actions
  - AI Chat Assistant for real-time guidance
  - In-app notifications for every status change
  - Awareness content (Dos & Don'ts for waste segregation)

WORKER MODULE
  - View assigned tasks with location and priority
  - Accept > Start > Upload Proof > Complete workflow
  - Upload completion proof with image + GPS coordinates
  - View task history
  - Receive notifications on new assignments

ADMIN MODULE
  - Dashboard with real-time KPIs
  - Review, verify, or reject complaints
  - Assign complaints to workers
  - Verify completed tasks with proof review
  - Manage users — activate/deactivate workers and citizens
  - Manage tokens — manual adjustments with audit trail
  - Analytics — complaints by status, category, priority, ward
  - Waste Hotspots — map-based density visualization
  - Audit Logs — every sensitive action is logged

AI CIVIC ASSISTANT
  - Conversational help for citizens, workers, and admins
  - Context-aware (uses your own complaint and wallet data)
  - Powered by Groq's openai/gpt-oss-120b
  - Never invents data — if info is missing, it says so
  - Never exposes another user's private data
  - Runs only on the server — API key never touches the browser


================================================================
  ARCHITECTURE (High Level)
================================================================

  BROWSER (HTML + CSS + Vanilla JS)
      |
      | fetch() / JSON
      v
  FLASK BACKEND
      Routes  >  Services  >  Repositories
                    |
                    v
              SQLite (swachh_vatika.db)

      AI Service  >  Groq API (server-side only)

  - Routes handle HTTP, auth, and validation
  - Services own the business rules
  - Repositories own every SQL query
  - SQLite is the single source of truth


================================================================
  LOCAL SETUP (6 Steps)
================================================================

1. CLONE THE REPOSITORY
     git clone https://github.com/shukla-rishabh12/Swachh_Vatika.git
     cd Swachh_Vatika

2. CREATE A VIRTUAL ENVIRONMENT
     python -m venv .venv

   Activate it:
     Windows     :  .\.venv\Scripts\Activate.ps1
     Mac / Linux :  source .venv/bin/activate

3. INSTALL DEPENDENCIES
     pip install -r requirements.txt

4. CONFIGURE ENVIRONMENT VARIABLES
   Copy .env.example to .env and fill in:

     FLASK_ENV=development
     SECRET_KEY=<random-long-string>
     DATABASE_PATH=database/swachh_vatika.db
     GROQ_API_KEY=<your-groq-api-key>
     GROQ_MODEL=openai/gpt-oss-120b
     UPLOAD_FOLDER=uploads
     MAX_UPLOAD_SIZE_MB=5
     CORS_ORIGINS=http://127.0.0.1:5000,http://localhost:5000

   Get a free Groq API key: https://console.groq.com/keys

5. SEED THE DATABASE
     python database/seed.py

   This creates all demo data automatically.

6. RUN THE APP
     python app.py

   Open: http://127.0.0.1:5000


================================================================
  DEPLOYMENT (Render)
================================================================

The project is deployment-ready for Render with automatic seeding.

QUICK DEPLOY STEPS
  1. Push the repo to GitHub
  2. Go to https://render.com > New Web Service
  3. Connect your GitHub repo
  4. Use these settings:

       Runtime         :  Python 3
       Build Command   :  pip install -r requirements.txt
       Start Command   :  gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

  5. Add environment variables:

       FLASK_ENV       :  production
       SECRET_KEY      :  <auto-generate>
       GROQ_API_KEY    :  <your key>
       GROQ_MODEL      :  openai/gpt-oss-120b
       CORS_ORIGINS    :  *

  6. Click Create Web Service

The _auto_seed_if_empty() function in app.py will automatically
seed the database on first deploy.


KEEPING THE SERVICE AWAKE (Free Tier)
  Render free tier sleeps after 15 minutes of inactivity.

  To keep it alive:
    1. Sign up at https://uptimerobot.com (free)
    2. Add an HTTP monitor for:
         https://swachh-vatika.onrender.com/health
    3. Set interval to 5 minutes

  This prevents cold starts and keeps the demo snappy.


================================================================
  SECURITY PRACTICES
================================================================

  - Passwords hashed with Werkzeug (PBKDF2-SHA256)
  - Session-based auth — no JWT in localStorage
  - Role authorization enforced on backend
  - Object-level ownership checks (citizens see only own data)
  - File upload validation (MIME, extension, size)
  - SQL parameterized queries — no SQL injection
  - Groq API key never leaves the server
  - Audit logging for sensitive admin actions
  - Idempotent token rewards — no duplicate rewards


================================================================
  DESIGN PRINCIPLES
================================================================

  - Mobile-first citizen UI (most users are on phones)
  - Desktop-first admin console (data-heavy screens)
  - Green theme reflecting cleanliness and civic pride
  - Rounded cards, soft shadows, clear hierarchy
  - No external CSS frameworks — all custom, lightweight


================================================================
  END-TO-END TEST FLOW
================================================================

  1.  Login as Citizen     :  citizen@example.com / citizen123
  2.  Report a waste       :  photo + location + category
  3.  Logout
  4.  Login as Admin       :  admin@example.com / admin123
  5.  Verify the complaint
  6.  Assign it to a worker
  7.  Logout
  8.  Login as Worker      :  worker@example.com / worker123
  9.  Accept > Start > Upload Proof > Complete
  10. Logout
  11. Login as Admin
  12. Verify the task
  13. Complaint auto-closes > Tokens credited to citizen
  14. Login as Citizen
  15. Check Wallet and Notifications
  16. Open AI Chat and ask: "What's the status of my complaint?"

That is the entire Swachh_Vatika lifecycle.


================================================================
  API OVERVIEW
================================================================

All endpoints live under /api/v1/

  AUTH
    POST   /auth/login
    POST   /auth/register
    POST   /auth/logout
    GET    /auth/me

  COMPLAINTS
    POST   /complaints
    GET    /complaints/my
    GET    /complaints/<id>

  PICKUPS
    POST   /pickups
    GET    /pickups/my

  TASKS
    GET    /tasks/my
    POST   /tasks/<id>/accept
    POST   /tasks/<id>/start
    POST   /tasks/<id>/complete
    POST   /tasks/<id>/proof

  TOKENS
    GET    /tokens/wallet
    GET    /tokens/transactions

  NOTIFICATIONS
    GET    /notifications
    POST   /notifications/<id>/read
    POST   /notifications/read-all

  AI CHAT
    POST   /ai/chat

  ADMIN
    GET    /admin/dashboard
    GET    /admin/complaints
    PATCH  /admin/complaints/<id>/status
    POST   /admin/complaints/<id>/verify
    POST   /admin/complaints/<id>/reject
    DELETE /admin/complaints/<id>
    POST   /admin/tasks/assign
    GET    /admin/tasks
    POST   /admin/tasks/<id>/verify
    GET    /admin/tokens
    POST   /admin/tokens/adjust
    GET    /admin/analytics/summary
    GET    /admin/hotspots

  AUDIT
    GET    /audit

STANDARD RESPONSE FORMAT

  Success:
    {
      "success": true,
      "data": { ... },
      "message": "Operation successful."
    }

  Error:
    {
      "success": false,
      "data": null,
      "message": "Human readable error.",
      "error": { "code": "ERROR_CODE" }
    }


================================================================
  DATABASE SCHEMA (Highlights)
================================================================

  users                      Auth + role (CITIZEN / WORKER / ADMIN)
  profiles                   User details (name, phone, address)
  wards                      Municipal zone groupings
  complaints                 Core entity — waste reports
  complaint_images           Photo attachments
  complaint_status_history   Full audit trail of status changes
  pickup_requests            Scheduled pickups
  tasks                      Field operations assigned to workers
  task_proofs                Completion proofs
  token_wallets              SwachhToken balances
  token_transactions         Ledger (EARN/SPEND/ADJUSTMENT/REVERSAL)
  notifications              In-app alerts
  ai_conversations           AI chat sessions
  ai_messages                Individual chat messages
  audit_logs                 Sensitive admin actions
  system_settings            Configurable business values


================================================================
  ENVIRONMENT VARIABLES REFERENCE
================================================================

  FLASK_ENV            Required : No       Default : development
                       Values   : development / production / testing

  SECRET_KEY           Required : Yes      Flask session encryption key

  DATABASE_PATH        Required : No       Default : database/swachh_vatika.db
                       (Auto switches to /var/data on Render)

  GROQ_API_KEY         Required : Yes (for AI)
                       Get free key: https://console.groq.com/keys

  GROQ_MODEL           Required : No
                       Default  : openai/gpt-oss-120b

  UPLOAD_FOLDER        Required : No       Default : uploads

  MAX_UPLOAD_SIZE_MB   Required : No       Default : 5

  CORS_ORIGINS         Required : No
                       Default  : http://127.0.0.1:5000,http://localhost:5000


================================================================
  CONTRIBUTING RULES
================================================================

  - Keep the tech stack locked (no React, no Node, no Tailwind)
  - Follow the route > service > repository architecture
  - Every feature must include loading, empty, and error states
  - Every API must follow the standard response envelope


================================================================
  LICENSE
================================================================

  MIT License — free to use, modify, and distribute.


================================================================
  CONTACT & LINKS
================================================================

  GitHub Repo    :  https://github.com/shukla-rishabh12/Swachh_Vatika
  Live Demo      :  https://swachh-vatika.onrender.com
  Groq Console   :  https://console.groq.com/keys
  Render         :  https://render.com
  UptimeRobot    :  https://uptimerobot.com


================================================================
  Swachh_Vatika
  Because a clean city is a shared responsibility.
================================================================
