# Database and Blockchain Setup Guide

This guide explains how to set up PostgreSQL (Supabase) and blockchain integration for MediGuard AI.

## Prerequisites

1. A Supabase account (free tier available at https://supabase.com)
2. An Ethereum/Polygon wallet with testnet ETH/MATIC (for blockchain)
3. An RPC provider account (Infura, Alchemy, etc.) for blockchain access

## Step 1: Set Up Supabase Database

1. **Create a Supabase Project**
   - Go to https://supabase.com and create a new project
   - Wait for the project to be provisioned (takes ~2 minutes)

2. **Get Database Connection String**
   - Go to Project Settings → Database
   - Find "Connection string" section
   - Copy the "URI" connection string (starts with `postgresql://`)
   - Replace `[YOUR-PASSWORD]` with your database password

3. **Run Database Schema**
   - Option A: Use Supabase SQL Editor
     - Go to SQL Editor in Supabase dashboard
     - Copy contents of `backend/database/schema.sql`
     - Paste and run in SQL Editor
   
   - Option B: Use Migration Script
     ```bash
     cd backend
     python database/migrate.py
     ```

## Step 2: Configure Environment Variables

1. **Create `.env` file** in project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Fill in Database Configuration**:
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres
   SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
   SUPABASE_KEY=[YOUR-ANON-KEY]
   ```

3. **Fill in Blockchain Configuration** (Optional - for blockchain commits):
   ```env
   BLOCKCHAIN_RPC_URL=https://sepolia.infura.io/v3/[YOUR-INFURA-PROJECT-ID]
   BLOCKCHAIN_PRIVATE_KEY=[YOUR-PRIVATE-KEY-WITHOUT-0x-PREFIX]
   BLOCKCHAIN_NETWORK=sepolia
   ```

   **Important**: 
   - Use a **testnet** (Sepolia for Ethereum, Mumbai for Polygon) for development
   - Create a **separate wallet** for this purpose - do NOT use your main wallet
   - Keep your private key **secret** - never commit it to git

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `sqlalchemy>=2.0.0` - Database ORM
- `asyncpg>=0.29.0` - Async PostgreSQL driver
- `psycopg2-binary>=2.9.9` - PostgreSQL adapter
- `python-dotenv>=1.0.0` - Environment variable management
- `web3>=6.15.0` - Ethereum/Polygon interaction
- `eth-account>=0.10.0` - Ethereum account management

## Step 4: Verify Setup

1. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```

2. **Check health endpoint**:
   ```bash
   curl http://localhost:8000/api/health
   ```

   Should return:
   ```json
   {
     "status": "healthy",
     "prediction_service": true,
     "explainability_service": true,
     "database": true,
     "blockchain": true  // or false if not configured
   }
   ```

## How It Works

### Hash Chain
- Every prediction is automatically added to a hash chain
- Each hash links to the previous hash, creating an immutable chain
- Hash chain is stored in PostgreSQL database
- Provides immediate audit trail and immutability

### Blockchain Integration
- Periodically (default: every 24 hours), the root hash of the chain is committed to blockchain
- This provides external verification and non-repudiation
- Transaction hash and block number are stored in the database
- Can verify transactions on blockchain explorers (Etherscan, Polygonscan)

### User Management
- Frontend now uses API-based user creation instead of localStorage
- User IDs are generated server-side and stored in sessionStorage
- Each user can have multiple predictions tracked in the database

## API Endpoints

### New Endpoints

- `POST /api/users/create` - Create a new user
- `GET /api/users/{user_id}` - Get user information
- `GET /api/hash-chain/verify` - Verify hash chain integrity
- `GET /api/blockchain/verify/{tx_hash}` - Verify blockchain transaction

### Updated Endpoints

All prediction storage endpoints now use PostgreSQL:
- `POST /api/predictions/save` - Saves with hash chain
- `GET /api/predictions` - Queries from PostgreSQL
- `GET /api/predictions/stats` - Aggregates from PostgreSQL

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check Supabase project is active
- Ensure password is URL-encoded if it contains special characters

### Blockchain Issues
- Verify RPC URL is correct and accessible
- Check wallet has testnet ETH/MATIC for gas fees
- Verify private key format (should not include `0x` prefix)
- Blockchain service will fail gracefully if not configured

### Migration Issues
- If tables already exist, schema.sql uses `CREATE TABLE IF NOT EXISTS`
- Can safely re-run migration script
- Check Supabase logs for SQL errors

## Production Considerations

1. **Use Environment Variables**: Never commit `.env` file
2. **Use Mainnet**: Switch to mainnet only when ready (costs real money)
3. **Database Backups**: Set up Supabase automatic backups
4. **Connection Pooling**: Consider using Supabase connection pooling
5. **Security**: Use Supabase Row Level Security (RLS) for multi-tenant scenarios
6. **Monitoring**: Set up alerts for blockchain transaction failures

