#!/usr/bin/env python3
"""
Diagnostic script to test Supabase connection and permissions
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("SUPABASE CONNECTION DIAGNOSTIC TEST")
print("=" * 80)

# Check environment variables
print("\n1. Checking Environment Variables:")
print("-" * 80)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if supabase_url:
    print(f"✓ SUPABASE_URL is set: {supabase_url[:50]}...")
else:
    print("✗ SUPABASE_URL is NOT set!")
    sys.exit(1)

if supabase_key:
    print(f"✓ SUPABASE_SERVICE_ROLE_KEY is set: {supabase_key[:20]}...")
else:
    print("✗ SUPABASE_SERVICE_ROLE_KEY is NOT set!")
    sys.exit(1)

# Test Supabase connection
print("\n2. Testing Supabase Connection:")
print("-" * 80)

try:
    from supabase import create_client, Client
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✓ Supabase client created successfully")
except Exception as e:
    print(f"✗ Error creating Supabase client: {e}")
    sys.exit(1)

# Test read permission
print("\n3. Testing READ Permission (fetching 1 job):")
print("-" * 80)

try:
    response = supabase.table("jobs").select("job_id").limit(1).execute()
    if response.data is not None:
        print(f"✓ READ permission works. Got {len(response.data)} record(s)")
    elif hasattr(response, 'error') and response.error:
        print(f"✗ READ permission denied: {response.error}")
    else:
        print(f"✓ READ permission works (empty result). Response: {response}")
except Exception as e:
    print(f"✗ Error during READ test: {e}")
    import traceback
    traceback.print_exc()

# Test write permission with a test record
print("\n4. Testing WRITE Permission (attempting upsert):")
print("-" * 80)

test_job = {
    "job_id": "test_connection_check_12345",
    "job_title": "Test Job",
    "company": "Test Company",
    "description": "Test Description",
    "provider": "test",
    "location": "Test Location",
    "level": "Entry",
    "status": "new",
    "job_state": "new",
    "is_active": True
}

try:
    response = supabase.table("jobs").upsert([test_job]).execute()
    
    if hasattr(response, 'error') and response.error:
        print(f"✗ WRITE (upsert) permission denied: {response.error}")
        print(f"   Error message: {response.error}")
    elif hasattr(response, 'data') and response.data:
        print(f"✓ WRITE (upsert) permission works!")
        print(f"   Successfully wrote test record")
        
        # Try to delete the test record
        print("\n5. Cleaning up test record:")
        print("-" * 80)
        try:
            delete_response = supabase.table("jobs").delete().eq("job_id", "test_connection_check_12345").execute()
            print("✓ Test record deleted successfully")
        except Exception as del_e:
            print(f"⚠ Could not delete test record: {del_e}")
    else:
        print(f"Response: {response}")
        if hasattr(response, 'data'):
            print(f"✓ WRITE appears to work. Data: {response.data}")
        
except Exception as e:
    print(f"✗ Error during WRITE test: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 80)
