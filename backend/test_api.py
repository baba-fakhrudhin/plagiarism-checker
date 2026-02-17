"""
Comprehensive API Testing Script
Run this to verify all backend endpoints are working
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}

# Test credentials
TEST_EMAIL = f"testuser{int(time.time())}@example.com"
TEST_USERNAME = f"testuser{int(time.time())}"
TEST_PASSWORD = "TestPassword123"

# Global variables to store tokens and IDs
auth_token = None
user_id = None
document_id = None
analysis_id = None

def print_test(test_name, response, expected_status):
    """Print test results"""
    status = "✓ PASS" if response.status_code == expected_status else "✗ FAIL"
    print(f"\n{status} - {test_name}")
    print(f"  Status: {response.status_code} (Expected: {expected_status})")
    try:
        print(f"  Response: {json.dumps(response.json(), indent=2)[:200]}...")
    except:
        print(f"  Response: {response.text[:200]}")

def test_signup():
    """Test user signup"""
    global auth_token, user_id
    
    print("\n" + "="*60)
    print("TESTING AUTHENTICATION")
    print("="*60)
    
    payload = {
        "email": TEST_EMAIL,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/signup",
        json=payload,
        headers=HEADERS
    )
    
    print_test("POST /auth/signup", response, 201)
    
    if response.status_code == 201:
        data = response.json()
        auth_token = data.get('access_token')
        user_id = data.get('user', {}).get('id')
        print(f"  Token: {auth_token[:20]}...")
        print(f"  User ID: {user_id}")
        return True
    return False

def test_login():
    """Test user login"""
    global auth_token, user_id
    
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=payload,
        headers=HEADERS
    )
    
    print_test("POST /auth/login", response, 200)
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get('access_token')
        user_id = data.get('user', {}).get('id')
        return True
    return False

def test_get_profile():
    """Test get user profile"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers=headers
    )
    
    print_test("GET /auth/me", response, 200)
    return response.status_code == 200

def test_upload_text():
    """Test text upload"""
    global document_id
    
    print("\n" + "="*60)
    print("TESTING FILE UPLOAD")
    print("="*60)
    
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    payload = {
        "text": "This is a sample document for plagiarism detection. " * 20,
        "title": "Sample Document"
    }
    
    response = requests.post(
        f"{BASE_URL}/upload/text",
        json=payload,
        headers=headers
    )
    
    print_test("POST /upload/text", response, 201)
    
    if response.status_code == 201:
        data = response.json()
        document_id = data.get('document', {}).get('id')
        print(f"  Document ID: {document_id}")
        return True
    return False

def test_list_documents():
    """Test listing documents"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    response = requests.get(
        f"{BASE_URL}/upload/documents",
        headers=headers
    )
    
    print_test("GET /upload/documents", response, 200)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Total Documents: {data.get('total')}")
        print(f"  Documents: {len(data.get('documents', []))}")
    return response.status_code == 200

def test_get_document():
    """Test get document details"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    response = requests.get(
        f"{BASE_URL}/upload/document/{document_id}",
        headers=headers
    )
    
    print_test(f"GET /upload/document/{document_id}", response, 200)
    return response.status_code == 200

def test_start_analysis():
    """Test start plagiarism analysis"""
    global analysis_id
    
    print("\n" + "="*60)
    print("TESTING PLAGIARISM ANALYSIS")
    print("="*60)
    
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    payload = {"document_id": document_id}
    
    response = requests.post(
        f"{BASE_URL}/analysis/start",
        json=payload,
        headers=headers
    )
    
    print_test("POST /analysis/start", response, 201)
    
    if response.status_code == 201:
        data = response.json()
        analysis_id = data.get('analysis', {}).get('id')
        print(f"  Analysis ID: {analysis_id}")
        return True
    return False

def test_check_analysis_status():
    """Test check analysis status"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    # Give it time to process
    print("  Waiting 5 seconds for analysis to process...")
    time.sleep(5)
    
    response = requests.get(
        f"{BASE_URL}/analysis/status/{analysis_id}",
        headers=headers
    )
    
    print_test(f"GET /analysis/status/{analysis_id}", response, 200)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Status: {data.get('status')}")
    return response.status_code == 200

def test_list_analyses():
    """Test listing analyses"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    response = requests.get(
        f"{BASE_URL}/analysis/list",
        headers=headers
    )
    
    print_test("GET /analysis/list", response, 200)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Total Analyses: {data.get('total')}")
    return response.status_code == 200

def test_get_results():
    """Test get analysis results"""
    headers = HEADERS.copy()
    headers['Authorization'] = f'Bearer {auth_token}'
    
    response = requests.get(
        f"{BASE_URL}/results/analysis/{analysis_id}",
        headers=headers
    )
    
    print_test(f"GET /results/analysis/{analysis_id}", response, 200)
    
    if response.status_code == 200:
        data = response.json()
        print(f"  Similarity Score: {data.get('overall_similarity')}")
        print(f"  AI Probability: {data.get('ai_generated_probability')}")
        print(f"  Matches: {data.get('total_matches')}")
    return response.status_code == 200

def test_database_connection():
    """Test database connection"""
    print("\n" + "="*60)
    print("TESTING DATABASE CONNECTION")
    print("="*60)
    
    try:
        from app import create_app, db
        app = create_app()
        with app.app_context():
            db.session.execute("SELECT 1")
            print("✓ PASS - Database Connection")
            print("  Successfully connected to PostgreSQL database")
            return True
    except Exception as e:
        print("✗ FAIL - Database Connection")
        print(f"  Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*80)
    print("PLAGIARISM CHECKER API - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {BASE_URL}")
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Signup", test_signup),
        ("User Login", test_login),
        ("Get Profile", test_get_profile),
        ("Upload Text", test_upload_text),
        ("List Documents", test_list_documents),
        ("Get Document", test_get_document),
        ("Start Analysis", test_start_analysis),
        ("Check Analysis Status", test_check_analysis_status),
        ("List Analyses", test_list_analyses),
        ("Get Results", test_get_results),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"✗ FAIL - {test_name}")
            print(f"  Exception: {str(e)}")
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

if __name__ == "__main__":
    run_all_tests()