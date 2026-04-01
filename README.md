# Nyelvcsere Közösség - Language Exchange Platform

A modern full-stack web application for connecting language mentors and students, enabling peer-to-peer language learning through structured sessions.

## Project Status 🚀

**Last Updated:** April 1, 2026

### Current Features ✅

#### Core Platform
- ✅ **User Authentication:** JWT-based login/registration with bcrypt password hashing
- ✅ **Guest Support:** Browse mentors and home page without authentication; booking requires login
- ✅ **Responsive Design:** Mobile-friendly UI with breakpoints for 820px, 760px, 520px screens
- ✅ **Role-Based Access:** Student and Mentor roles with different capabilities

#### Mentor System
- ✅ **Mentor Profiles:** Create and manage mentor language pairs (taught/learned languages)
- ✅ **Mentor Listing:** Search mentors by name, filter by language
- ✅ **Avatar Generation:** Automatic visual profiles using Dicebear API
- ✅ **Hover Effects:** Interactive card animations for better UX
- ✅ **Past-Time Blocking:** Prevent booking sessions in the past

#### Session Management
- ✅ **Session CRUD:** Create, read, update, and delete booking sessions
- ✅ **Status Tracking:** Sessions can be scheduled, completed, or canceled
- ✅ **Mentor Name Selector:** User-friendly dropdown instead of numeric IDs
- ✅ **Date/Time Validation:** Client-side validation prevents past bookings

#### Admin Features
- ✅ **User Dashboard:** View all platform users with role badges and avatars
- ✅ **Language Management:** Curated language list (English, Hungarian, German)
- ✅ **Demo Data:** Pre-seeded demo users for testing

### Pending Features 🚧

- 🔄 **Email Verification:** Email confirmation for new registrations
- 🔄 **Refresh Tokens:** Extended session support with token refresh mechanism
- 🔄 **Rate Limiting:** API rate limiting for abuse prevention
- 🔄 **Session Scheduling Validation:** Advanced conflict detection
- 🔄 **Progress Logging:** Track student progress across sessions

## Tech Stack

### Frontend
- **Framework:** Vue 3 with Composition API
- **Router:** Vue Router 4
- **HTTP Client:** Axios
- **Styling:** CSS3 (Grid/Flexbox)
- **Dev Server:** Vite (port 5173)

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Authentication:** JWT (python-jose, passlib)
- **Password Hashing:** bcrypt
- **CORS:** CORSMiddleware for cross-origin requests
- **Server:** Uvicorn (port 8000)

## Project Structure

```
Nyelvcsere_kozosseg/
├── backend/
│   ├── main.py              # FastAPI application, all routes
│   ├── models.py            # SQLAlchemy ORM models
│   ├── database.py          # SQLite session factory
│   ├── init_db.py           # Demo data initialization
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Root component with responsive header
│   │   ├── router/
│   │   │   └── index.js     # Route definitions and auth guards
│   │   └── views/
│   │       ├── HomeView.vue          # Landing page
│   │       ├── LoginView.vue         # Authentication
│   │       ├── RegisterView.vue      # User registration
│   │       ├── ProfileView.vue       # User profile & mentor settings
│   │       ├── MentorsView.vue       # Mentor listing & booking
│   │       ├── DashboardView.vue     # User administration
│   │       └── SessionsView.vue      # Session management
│   ├── package.json
│   └── vite.config.js
├── docs/                    # Documentation
├── prompts/                 # Agent customizations
└── README.md               # This file
```

## Database Schema

### User
- `id` (Integer, PK)
- `name` (String)
- `email` (String, unique)
- `hashed_password` (String)
- `role` (String: "student" | "mentor")

### Language
- `id` (Integer, PK)
- `name` (String, unique)

### MentorProfile
- `id` (Integer, PK)
- `user_id` (Integer, FK → User)
- `offered_language_id` (Integer, FK → Language)
- `requested_language_id` (Integer, FK → Language)
- `session_length_minutes` (Integer, default: 60)

### Session
- `id` (Integer, PK)
- `student_id` (Integer, FK → User)
- `mentor_profile_id` (Integer, FK → MentorProfile)
- `scheduled_time` (DateTime)
- `status` (String: "scheduled" | "completed" | "canceled")

### ProgressLog
- `id` (Integer, PK)
- `session_id` (Integer, FK → Session)
- `student_id` (Integer, FK → User)
- `notes` (String)
- `rating` (Integer, 1-5)

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database (includes demo data):**
   ```bash
   python init_db.py
   ```

   This creates `database.db` with:
   - Languages: English, Hungarian, German
   - Demo Mentor: `anna.mentor@example.com` / `demo123`
   - Demo Student: `peter.student@example.com` / `demo123`

5. **Start the backend server:**
   ```bash
   uvicorn main:app --reload
   ```
   Server runs at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   App runs at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```

## Running the Application

1. **Terminal 1 - Backend:**
   ```bash
   cd backend && venv\Scripts\activate && uvicorn main:app --reload
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd frontend && npm run dev
   ```

3. **Access the app:** Open `http://localhost:5173` in your browser

## API Endpoints Summary

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and receive JWT token
- `GET /users/me` - Get current user profile (includes `is_authenticated` flag for guests)

### User Management
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user by ID

### Mentor Profiles
- `GET /mentor-profiles` - List all mentor profiles
- `POST /mentor-profile/me` - Create mentor profile (for current user)
- `PUT /mentor-profile/me` - Update mentor profile (target languages)
- `GET /users/{user_id}/mentor-profile` - Get mentor info for user

### Sessions
- `POST /sessions` - Create new session (requires auth)
- `GET /sessions` - List all sessions (current user's sessions if not admin)
- `GET /sessions/{session_id}` - Get session details
- `PUT /sessions/{session_id}/status` - Update session status
- `DELETE /sessions/{session_id}` - Cancel session

### Languages
- `GET /languages` - List available languages

## Demo Credentials

After initialization, use these credentials to test:

| Role | Email | Password |
|------|-------|----------|
| Mentor | `anna.mentor@example.com` | `demo123` |
| Student | `peter.student@example.com` | `demo123` |

**Note:** Passwords are bcrypt-hashed. First login may require database reset:
```bash
# Delete existing database
rm database.db  # or del database.db on Windows
# Restart backend to reinitialize
```

## Frontend Routes

| Route | Protected | Description |
|-------|-----------|-------------|
| `/` | ❌ | Home page with hero and feature overview |
| `/login` | ❌ | User login page |
| `/register` | ❌ | User registration page |
| `/mentors` | ⚠️ | Mentor listing (guest-friendly, booking requires auth) |
| `/profile` | ✅ | User profile and mentor settings |
| `/sessions` | ✅ | Session management (CRUD) |
| `/dashboard` | ✅ | User administration |

**Legend:** ✅ = Requires authentication | ⚠️ = Partially protected | ❌ = Public

## Key Features Deep Dive

### Guest Access
- Non-authenticated users can view the home page and mentor listing
- Booking buttons display login prompts for guests
- Token stored in `localStorage` as `access_token`

### Responsive Design
- Mobile breakpoints at 820px and 520px
- Flex/Grid layouts adapt to screen size
- Header navigation collapses on smaller screens

### Session Validation
- Frontend prevents past-date selection via `<input type="datetime-local" :min="minDateTime">`
- Backend validates session times before creation
- Alert messages guide users to valid time slots

### Mentor Name Selection
- Sessions CRUD uses human-readable mentor names instead of profile IDs
- Dropdown populated from `GET /mentor-profiles` endpoint
- Selected mentor name displayed in session cards

## Known Issues & Limitations

1. **Token Key Inconsistency:** Some code paths reference both `token` and `access_token` from localStorage _(Medium Priority)_
2. **No Email Verification:** Registrations accepted without email confirmation _(Low Priority)_
3. **No Concurrent Session Limits:** Mentors can theoretically have unlimited overlapping sessions _(Medium Priority)_
4. **SQLite Limitation:** Not suitable for production multi-concurrent access _(Migrate to PostgreSQL for production)_

## Contributing

When adding features:
1. Update both backend (FastAPI) and frontend (Vue 3) changes
2. Run demo data initialization: `python backend/init_db.py`
3. Test with demo credentials
4. Update this README with new routes/features

## License

This project is created for the Nyelvcsere Közösség language exchange community.

---

**Last Updated:** April 1, 2026 | **Status:** Fully Functional with Responsive UI & Authentication
