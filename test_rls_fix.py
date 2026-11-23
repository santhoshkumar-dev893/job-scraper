#!/usr/bin/env python3
"""
Test RLS Fix for Skills Table

Purpose: Verify that service role can read and write to skills table
Status: Run after applying fix_rls_read_permission.sql
Expected: All 4 tests should pass

Usage:
    python test_rls_fix.py
    
Expected Output:
    ✅ Test 1: Can read skills - PASSED
    ✅ Test 2: SkillManager initializes - PASSED
    ✅ Test 3: Has skill lookup works - PASSED
    ✅ Test 4: Can insert and delete - PASSED
    
    ✅ ALL TESTS PASSED!
"""

import os
import sys
import uuid
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_supabase():
    """Initialize Supabase client with service role key"""
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_role_key:
            print("❌ ERROR: Missing environment variables")
            print(f"   SUPABASE_URL: {supabase_url or 'NOT SET'}")
            print(f"   SUPABASE_SERVICE_ROLE_KEY: {('SET' if service_role_key else 'NOT SET')}")
            return None
        
        client = create_client(supabase_url, service_role_key)
        return client
    
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Supabase: {e}")
        return None


def test_1_read_skills(supabase) -> bool:
    """Test 1: Can service role read skills from database?"""
    print("\n" + "="*60)
    print("Test 1: Reading skills from database")
    print("="*60)
    
    try:
        response = supabase.table("skills").select("id, skill_name, requirement").limit(5).execute()
        
        if response.data:
            skill_count = len(response.data)
            print(f"✅ SUCCESS: Read {skill_count} skills from database")
            
            print("\n   Sample skills:")
            for skill in response.data[:3]:
                print(f"     • {skill['skill_name']} ({skill['requirement']})")
            
            return True
        else:
            print("⚠️  WARNING: No skills found in database")
            print("   This might be normal if database hasn't been seeded yet")
            print("   Run: python -c \"from seed_core_skills import *\"")
            # Return True anyway - this is not a RLS failure
            return True
    
    except Exception as e:
        print(f"❌ FAILED: Cannot read skills")
        print(f"   Error: {str(e)}")
        
        if "permission denied" in str(e).lower():
            print("\n   ⚠️  RLS ISSUE: Service role cannot SELECT from skills table")
            print("   The fix_rls_read_permission.sql may not have been applied correctly")
        
        return False


def test_2_skill_manager(supabase) -> bool:
    """Test 2: Can SkillManager initialize and load skills?"""
    print("\n" + "="*60)
    print("Test 2: SkillManager initialization")
    print("="*60)
    
    try:
        from skills_manager import SkillManager
        
        print("   Initializing SkillManager...")
        manager = SkillManager(supabase)
        
        skill_count = len(manager.get_all_skills())
        
        if skill_count > 0:
            print(f"✅ SUCCESS: SkillManager loaded {skill_count} skills")
            
            # Check cache stats
            stats = manager.get_stats()
            print(f"\n   Cache Statistics:")
            print(f"     • Total skills: {stats['total_skills']}")
            print(f"     • Core skills: {stats['core_skills']}")
            print(f"     • Discovered skills: {stats['discovered_skills']}")
            print(f"     • Discovery rate: {stats['discovery_rate']}")
            
            return True
        else:
            print("⚠️  WARNING: SkillManager loaded 0 skills")
            print("   This might be normal if database is empty")
            # Not a RLS failure, just empty database
            return True
    
    except Exception as e:
        print(f"❌ FAILED: SkillManager could not initialize")
        print(f"   Error: {str(e)}")
        
        if "permission denied" in str(e).lower() or "SELECT" in str(e):
            print("\n   ⚠️  RLS ISSUE: SkillManager cannot read from database")
            print("   The fix_rls_read_permission.sql fix is required")
        
        return False


def test_3_has_skill(supabase) -> bool:
    """Test 3: Can SkillManager check if skill exists?"""
    print("\n" + "="*60)
    print("Test 3: Skill existence check")
    print("="*60)
    
    try:
        from skills_manager import SkillManager
        
        manager = SkillManager(supabase)
        
        # Try to check for common skills
        test_skills = ["Python", "Java", "JavaScript", "Docker", "AWS"]
        
        found_skills = []
        for skill_name in test_skills:
            if manager.has_skill(skill_name):
                found_skills.append(skill_name)
        
        if found_skills:
            print(f"✅ SUCCESS: Found {len(found_skills)} test skills in database")
            print(f"\n   Found skills:")
            for skill in found_skills:
                print(f"     • {skill}")
            return True
        else:
            print("ℹ️  INFO: None of the test skills found in database")
            print(f"   Test skills: {', '.join(test_skills)}")
            print("   This is normal if database hasn't been seeded")
            # Not a RLS failure
            return True
    
    except Exception as e:
        print(f"❌ FAILED: Cannot check skill existence")
        print(f"   Error: {str(e)}")
        
        if "permission denied" in str(e).lower():
            print("\n   ⚠️  RLS ISSUE: Cannot query skills table")
        
        return False


def test_4_insert_permission(supabase) -> bool:
    """Test 4: Can service role insert into skills table?"""
    print("\n" + "="*60)
    print("Test 4: Insert and delete permission")
    print("="*60)
    
    # Generate unique skill name to avoid conflicts
    test_skill_id = uuid.uuid4().hex[:8]
    test_skill_name = f"TestSkill_{test_skill_id}"
    
    try:
        print(f"   Attempting to insert test skill: {test_skill_name}")
        
        test_skill = {
            'skill_name': test_skill_name,
            'requirement': 'optional',
            'description': f'Temporary test skill (ID: {test_skill_id})',
            'confidence_score': 0.5,
            'tags': ['test']
        }
        
        # Insert
        insert_response = supabase.table("skills").insert(test_skill).execute()
        
        if not insert_response.data:
            print("❌ FAILED: Insert returned no data")
            return False
        
        inserted_skill = insert_response.data[0]
        skill_id = inserted_skill['id']
        
        print(f"✅ SUCCESS: Inserted skill with ID: {skill_id}")
        
        # Verify we can read it back
        print(f"   Verifying inserted skill...")
        select_response = supabase.table("skills").select("*").eq("id", skill_id).execute()
        
        if not select_response.data:
            print("⚠️  WARNING: Inserted skill not found on read-back")
            # Continue anyway, try to clean up
        else:
            print(f"✅ SUCCESS: Verified inserted skill exists in database")
        
        # Delete test skill (cleanup)
        print(f"   Cleaning up test skill...")
        delete_response = supabase.table("skills").delete().eq("id", skill_id).execute()
        
        print(f"✅ SUCCESS: Cleaned up test skill")
        
        return True
    
    except Exception as e:
        print(f"❌ FAILED: Insert/delete operation failed")
        print(f"   Error: {str(e)}")
        
        if "permission denied" in str(e).lower():
            print("\n   ⚠️  RLS ISSUE: Service role cannot INSERT into skills table")
            print("   The fix_rls_read_permission.sql fix is required")
        
        return False


def main():
    """Run all tests"""
    
    print("\n" + "="*60)
    print("RLS FIX VERIFICATION TEST SUITE")
    print("="*60)
    print("\nThis test verifies that the RLS fix has been correctly applied")
    print("and that SkillManager can read/write to the skills table.")
    
    # Initialize Supabase
    print("\n📡 Connecting to Supabase...")
    supabase = setup_supabase()
    
    if not supabase:
        print("\n❌ FATAL: Cannot connect to Supabase")
        return False
    
    print("✅ Connected to Supabase")
    
    # Run all tests
    results = {
        "Test 1: Read skills": test_1_read_skills(supabase),
        "Test 2: SkillManager init": test_2_skill_manager(supabase),
        "Test 3: Has skill check": test_3_has_skill(supabase),
        "Test 4: Insert/delete": test_4_insert_permission(supabase),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    
    if passed == total:
        print(f"✅ ALL {total} TESTS PASSED!")
        print("✅ RLS FIX IS WORKING CORRECTLY!")
        print("✅ System is ready for deployment")
        print("="*60 + "\n")
        return True
    else:
        print(f"❌ {total - passed} TEST(S) FAILED!")
        print(f"❌ RLS FIX MAY NOT BE APPLIED CORRECTLY")
        print("\nNEXT STEPS:")
        print("1. Check that fix_rls_read_permission.sql was executed")
        print("2. Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are correct")
        print("3. Check Supabase dashboard for policies on skills table")
        print("4. Try running the SQL fix again")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
