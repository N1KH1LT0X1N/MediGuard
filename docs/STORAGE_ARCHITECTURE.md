# Storage Architecture - Supabase Integration

## Overview

All persistent data is stored in Supabase (PostgreSQL). sessionStorage is only used for temporary session management.

## Data Storage Locations

### ✅ Stored in Supabase (PostgreSQL)

1. **Users Table** (`users`)
   - `id` (TEXT, PRIMARY KEY) - User ID
   - `created_at` (TIMESTAMPTZ) - User creation timestamp
   - `updated_at` (TIMESTAMPTZ) - Last update timestamp
   - `preferences` (JSONB) - User preferences (theme, notifications, language, etc.)
   - `metadata` (JSONB) - Additional user metadata

2. **Predictions Table** (`predictions`)
   - `id` (TEXT, PRIMARY KEY) - Prediction UUID
   - `user_id` (TEXT, FOREIGN KEY → users.id) - Links to user
   - `timestamp` (TIMESTAMPTZ) - Prediction timestamp
   - `source` (TEXT) - Source: manual, pdf, csv, image
   - `input_features` (JSONB) - Raw 24 feature values
   - `prediction_result` (JSONB) - Full prediction response (disease, probabilities, explainability)
   - `created_at` (TIMESTAMPTZ) - Record creation timestamp

3. **Hash Chain Table** (`hash_chain`)
   - `id` (SERIAL, PRIMARY KEY)
   - `prediction_id` (TEXT, FOREIGN KEY → predictions.id) - Links to prediction
   - `previous_hash` (TEXT) - Previous hash in chain
   - `current_hash` (TEXT, UNIQUE) - Current hash
   - `block_timestamp` (TIMESTAMPTZ) - Hash timestamp
   - `blockchain_tx_hash` (TEXT) - Blockchain transaction hash (if committed)
   - `blockchain_block_number` (BIGINT) - Blockchain block number (if committed)
   - `created_at` (TIMESTAMPTZ) - Record creation timestamp

### ⚠️ Temporary Session Storage (sessionStorage)

**Only used for:**
- `mediguard_user_id` - Current active user ID in this browser session

**Why sessionStorage?**
- Session-based: Cleared when browser tab closes
- Not persistent: Doesn't survive browser restarts
- Just for UI state: Tracks which user is currently active
- All actual data is in Supabase

**Migration Path:**
- User ID is created via API (`/api/users/create`) and stored in Supabase
- sessionStorage just holds the current session's user_id
- If sessionStorage is cleared, user can still access their data via user_id lookup

## API Endpoints for Data Management

### User Management
- `POST /api/users/create` - Create new user (stored in Supabase)
- `GET /api/users/{user_id}` - Get user info, preferences, and stats (from Supabase)
- `PUT /api/users/{user_id}/preferences` - Update user preferences (stored in Supabase)

### Prediction Management
- `POST /api/predictions/save` - Save prediction (stored in Supabase with hash chain)
- `GET /api/predictions` - Get predictions (from Supabase)
- `GET /api/predictions/user/{user_id}` - Get user's predictions (from Supabase)
- `GET /api/predictions/stats` - Get dashboard stats (aggregated from Supabase)

### Verification
- `GET /api/hash-chain/verify` - Verify hash chain integrity (from Supabase)
- `GET /api/blockchain/verify/{tx_hash}` - Verify blockchain transaction

## Data Flow

### User Creation Flow
```
Frontend: createUser() API call
    ↓
Backend: POST /api/users/create
    ↓
Supabase: INSERT INTO users (id, preferences, metadata)
    ↓
Response: { user_id, message }
    ↓
Frontend: Store user_id in sessionStorage (temporary)
```

### Prediction Flow
```
Frontend: User makes prediction
    ↓
Backend: POST /api/predict
    ↓
Backend: Auto-save via savePrediction()
    ↓
Supabase: 
  1. Ensure user exists (CREATE IF NOT EXISTS)
  2. INSERT INTO predictions
  3. INSERT INTO hash_chain (with hash calculation)
  4. Optional: Commit to blockchain (simulated or real)
    ↓
Response: { prediction_id, message }
```

### Data Retrieval Flow
```
Frontend: getUserPredictions(userId)
    ↓
Backend: GET /api/predictions/user/{user_id}
    ↓
Supabase: SELECT * FROM predictions WHERE user_id = ?
    ↓
Response: List of predictions (from Supabase)
```

## What's NOT in localStorage

**Nothing is stored in localStorage.** All persistent data is in Supabase:
- ✅ User accounts → Supabase `users` table
- ✅ User preferences → Supabase `users.preferences` JSONB
- ✅ Predictions → Supabase `predictions` table
- ✅ Hash chain → Supabase `hash_chain` table
- ✅ Dashboard stats → Calculated from Supabase data

## Migration from sessionStorage

If you need to migrate existing sessionStorage data:

1. **User ID**: Already handled - user_id is created via API and stored in Supabase
2. **Predictions**: Already saved to Supabase via `savePrediction()` API
3. **Preferences**: Use `PUT /api/users/{user_id}/preferences` to store in Supabase

## Frontend Usage

### Current Implementation
```javascript
// sessionStorage is ONLY for current session's user_id
const userId = sessionStorage.getItem('mediguard_user_id');

// All data operations use Supabase via API
await savePrediction(userId, features, result, source);
await getUserPredictions(userId);
await getDashboardStats(userId);
await updateUserPreferences(userId, preferences);
```

### Best Practice
- Use sessionStorage only for temporary UI state (current user_id)
- All persistent data goes through API → Supabase
- User can access their data even if sessionStorage is cleared (via user_id lookup)

## Database Schema

See `backend/database/schema.sql` for complete schema definition.

## Summary

✅ **All persistent data is in Supabase**
- Users, predictions, hash chain, preferences

✅ **sessionStorage is only for session management**
- Current active user_id (temporary, cleared on tab close)

✅ **No localStorage usage**
- Everything is backed by Supabase

✅ **User preferences supported**
- Stored in Supabase `users.preferences` JSONB field
- API endpoint: `PUT /api/users/{user_id}/preferences`

