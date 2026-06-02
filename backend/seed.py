import requests
import json

BACKEND_URL = "http://127.0.0.1:8000"
TEAM_TOKEN = "youseeit-dev-token"

headers = {
    "Authorization": f"Bearer {TEAM_TOKEN}",
    "Content-Type": "application/json"
}

bugs = [
    # ─── Null Pointer / None checks ───
    {
        "title": "Null Pointer on Empty User List",
        "description": "Calling .get(0) on an empty list throws NullPointerException.",
        "rootCause": "List was never checked for empty before accessing first element.",
        "fixDescription": "Added isEmpty() check before calling .get(0). Return empty result if list is empty.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/UserService.java"
    },
    {
        "title": "None Dereference on Missing Config Key",
        "description": "Accessing config['db_host'] raises KeyError when key is missing from config file.",
        "rootCause": "Config file was optional but code assumed all keys were present.",
        "fixDescription": "Used config.get('db_host', 'localhost') with a default value fallback.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/config.py"
    },
    {
        "title": "Null Response from HTTP Client Not Handled",
        "description": "HTTP client returns null when server is unreachable. Code calls .status on null object.",
        "rootCause": "Network timeout was not handled — assumed response always returned.",
        "fixDescription": "Added null check on response before accessing .status. Return error state if null.",
        "severity": "critical",
        "fixedBy": "Son",
        "language": "typescript",
        "filePath": "src/apiClient.ts"
    },
    {
        "title": "Undefined Variable Access in Async Callback",
        "description": "Variable declared outside async callback is undefined inside it due to closure timing.",
        "rootCause": "Variable was reassigned after the async call was initiated but before callback fired.",
        "fixDescription": "Captured variable value at call time using const inside the async block.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "typescript",
        "filePath": "src/handler.ts"
    },
    {
        "title": "None Check Missing on Database Query Result",
        "description": "db.query().first() returns None when no record found. Accessing .id on None crashes.",
        "rootCause": "Assumed record always exists in database without checking return value.",
        "fixDescription": "Added if result is None: raise HTTPException(404) before accessing result fields.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "backend/main.py"
    },

    # ─── Off-by-one errors ───
    {
        "title": "Off-by-One in Pagination Offset",
        "description": "Page 1 returns items 1-20 but page 2 returns items 20-40, duplicating item 20.",
        "rootCause": "Offset calculated as page * limit instead of (page - 1) * limit.",
        "fixDescription": "Changed offset formula to (page - 1) * limit. Added test for page boundary.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "backend/main.py"
    },
    {
        "title": "Array Index Out of Bounds in Loop",
        "description": "Loop iterates to array.length inclusive, causing ArrayIndexOutOfBoundsException on last element.",
        "rootCause": "Used i <= array.length instead of i < array.length in for loop condition.",
        "fixDescription": "Changed condition to i < array.length. Added unit test for last element access.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/DataProcessor.java"
    },
    {
        "title": "Sliding Window Misses Last Element",
        "description": "Sliding window algorithm stops one element short of end of array.",
        "rootCause": "Window end condition used strict less-than instead of less-than-or-equal.",
        "fixDescription": "Changed while right < n to while right <= n to include last element.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/window.py"
    },
    {
        "title": "String Slice Off-by-One Drops Last Character",
        "description": "String trimming function drops the last character of the input string.",
        "rootCause": "Slice used str[0:len(str)-1] instead of str[0:len(str)].",
        "fixDescription": "Used str.strip() instead of manual slice. Added test with single-char strings.",
        "severity": "low",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/utils.py"
    },

    # ─── Race conditions ───
    {
        "title": "Race Condition on Shared Counter",
        "description": "Two threads increment shared counter simultaneously, causing lost updates.",
        "rootCause": "Counter increment was not atomic — read-modify-write was not synchronized.",
        "fixDescription": "Used AtomicInteger for counter. Wrapped increment in synchronized block.",
        "severity": "critical",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/Counter.java"
    },
    {
        "title": "Race Condition in File Write",
        "description": "Two async functions write to same file simultaneously, corrupting content.",
        "rootCause": "File write was not protected by a lock — both coroutines entered write section.",
        "fixDescription": "Added asyncio.Lock() around file write section. Only one coroutine writes at a time.",
        "severity": "critical",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/writer.py"
    },
    {
        "title": "Double Initialization Due to Race on Startup",
        "description": "Service initialized twice when two requests arrive simultaneously at startup.",
        "rootCause": "Initialization check (if not initialized) was not atomic.",
        "fixDescription": "Used a threading.Lock() to guard initialization block. Added initialized flag inside lock.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/service.py"
    },
    {
        "title": "Stale Cache Read After Concurrent Write",
        "description": "Cache returns stale value when another thread updates it simultaneously.",
        "rootCause": "Cache read and write were not synchronized — read saw pre-update value.",
        "fixDescription": "Used ReadWriteLock — multiple readers allowed, exclusive write lock on update.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/Cache.java"
    },

    # ─── Memory leaks ───
    {
        "title": "Event Listener Not Removed on Component Unmount",
        "description": "Window resize event listener accumulates on every component mount, causing memory leak.",
        "rootCause": "addEventListener called in useEffect without returning cleanup function.",
        "fixDescription": "Added return () => window.removeEventListener(...) cleanup in useEffect.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "typescript",
        "filePath": "src/ResizeHandler.tsx"
    },
    {
        "title": "Database Connection Not Closed After Query",
        "description": "Database connections accumulate and exhaust connection pool after extended use.",
        "rootCause": "Connection opened inside function but never closed — no finally block.",
        "fixDescription": "Wrapped connection in try/finally. Used context manager (with db.connect()) instead.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/db.py"
    },
    {
        "title": "Large Object Held in Global Variable",
        "description": "Parsed JSON response stored in global variable never released, growing with each request.",
        "rootCause": "Global cache had no eviction policy — appended every response without limit.",
        "fixDescription": "Replaced unbounded list with LRU cache (maxsize=100). Old entries evicted automatically.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/cache.py"
    },
    {
        "title": "Timer Not Cleared on Component Destroy",
        "description": "setInterval keeps running after component is destroyed, calling setState on unmounted component.",
        "rootCause": "clearInterval not called in component cleanup/destroy lifecycle.",
        "fixDescription": "Stored timer ID in ref. Called clearInterval(timerRef.current) in useEffect cleanup.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "typescript",
        "filePath": "src/PollingComponent.tsx"
    },

    # ─── API/HTTP errors ───
    {
        "title": "Missing Error Handling on Fetch Request",
        "description": "fetch() call has no catch block — unhandled promise rejection crashes the app.",
        "rootCause": "Developer assumed network requests always succeed.",
        "fixDescription": "Added .catch(error => ...) to fetch chain. Displayed error state in UI on failure.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "typescript",
        "filePath": "src/api.ts"
    },
    {
        "title": "API Rate Limit Not Handled",
        "description": "API returns 429 Too Many Requests but code treats it as success, processing empty response.",
        "rootCause": "Only checked for 200 status — did not handle non-200 responses.",
        "fixDescription": "Added status code check. On 429, implemented exponential backoff retry with max 3 attempts.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/client.py"
    },
    {
        "title": "CORS Error Blocks API Response",
        "description": "Frontend fetch call fails silently due to CORS policy — no error shown to user.",
        "rootCause": "Backend did not include CORS headers. Frontend fetch failed but error was swallowed.",
        "fixDescription": "Added fastapi-cors middleware with allowed origins. Added error boundary in frontend.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "backend/main.py"
    },
    {
        "title": "Request Timeout Not Set on External API Call",
        "description": "External API call hangs indefinitely when server is slow, blocking entire thread.",
        "rootCause": "No timeout parameter set on requests.get() call.",
        "fixDescription": "Added timeout=10 parameter to requests.get(). Added fallback response on TimeoutError.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/external.py"
    },

    # ─── Database/SQL errors ───
    {
        "title": "SQL Injection via Unsanitized Input",
        "description": "User input concatenated directly into SQL query string allows injection attack.",
        "rootCause": "Used string formatting to build query instead of parameterized queries.",
        "fixDescription": "Replaced string concat with SQLAlchemy parameterized queries. Input never touches SQL string.",
        "severity": "critical",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/queries.py"
    },
    {
        "title": "Transaction Not Rolled Back on Error",
        "description": "Partial database write committed when second insert fails, leaving data in inconsistent state.",
        "rootCause": "No transaction wrapping — each insert committed independently.",
        "fixDescription": "Wrapped both inserts in single transaction. Added rollback in except block.",
        "severity": "critical",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/db_ops.py"
    },
    {
        "title": "N+1 Query Problem in List Endpoint",
        "description": "Fetching 100 users runs 101 queries — 1 for list + 1 per user for related data.",
        "rootCause": "Related data fetched inside loop instead of using JOIN or eager loading.",
        "fixDescription": "Used SQLAlchemy joinedload() to fetch users and related data in single query.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "backend/main.py"
    },
    {
        "title": "Unique Constraint Violation on Concurrent Insert",
        "description": "Two simultaneous requests create duplicate records, violating unique constraint.",
        "rootCause": "Check-then-insert was not atomic — race window between check and insert.",
        "fixDescription": "Used INSERT ... ON CONFLICT DO NOTHING. Added database-level unique constraint.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/repository.py"
    },

    # ─── Type errors ───
    {
        "title": "String Passed Where Integer Expected",
        "description": "Function receives '42' as string from query param but tries to use it as integer for math.",
        "rootCause": "Query parameters are always strings in HTTP — no conversion applied.",
        "fixDescription": "Added int() conversion on input. Added Pydantic type validation to catch at boundary.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "backend/main.py"
    },
    {
        "title": "Boolean Coercion Bug in Conditional",
        "description": "Empty string '' evaluates to False in Python conditional, skipping valid empty input.",
        "rootCause": "Used if value: instead of if value is not None: — empty string is falsy.",
        "fixDescription": "Changed all None checks to explicit if value is not None: pattern.",
        "severity": "low",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/validator.py"
    },
    {
        "title": "Float Precision Error in Currency Calculation",
        "description": "0.1 + 0.2 == 0.30000000000000004 causes incorrect total in price calculation.",
        "rootCause": "Used float for currency instead of Decimal — IEEE 754 floating point precision issue.",
        "fixDescription": "Replaced float with Python Decimal. Used Decimal('0.1') + Decimal('0.2') for exact math.",
        "severity": "high",
        "fixedBy": "Son",
        "language": "python",
        "filePath": "src/pricing.py"
    },
    {
        "title": "Type Widening Loses Precision in Java",
        "description": "Long value silently truncated when assigned to int, causing wrong calculation result.",
        "rootCause": "Implicit narrowing cast from long to int — Java allows this without warning.",
        "fixDescription": "Changed variable type to long throughout calculation chain. Added assertion to catch overflow.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/Calculator.java"
    },
    {
        "title": "JSON Deserialization Ignores Unknown Fields",
        "description": "API adds new fields to response — old client silently ignores them, missing critical data.",
        "rootCause": "Deserialization configured to ignore unknown fields — new fields never reached the model.",
        "fixDescription": "Changed to FAIL_ON_UNKNOWN_PROPERTIES = true in dev. Added versioned API contract.",
        "severity": "medium",
        "fixedBy": "Son",
        "language": "java",
        "filePath": "src/ApiResponse.java"
    },
]

def seed():
    print(f"Seeding {len(bugs)} bugs...")
    success = 0
    failed = 0

    for i, bug in enumerate(bugs):
        try:
            response = requests.post(
                f"{BACKEND_URL}/learn",
                headers=headers,
                json=bug
            )
            if response.status_code == 200:
                print(f"✓ [{i+1}/{len(bugs)}] {bug['title']}")
                success += 1
            else:
                print(f"✗ [{i+1}/{len(bugs)}] {bug['title']} — {response.status_code}: {response.text}")
                failed += 1
        except Exception as e:
            print(f"✗ [{i+1}/{len(bugs)}] {bug['title']} — Error: {e}")
            failed += 1

    print(f"\nDone! {success} succeeded, {failed} failed.")

if __name__ == "__main__":
    seed()