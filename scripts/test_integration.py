import asyncio
import httpx
import time
import uuid

BASE_URL = "http://localhost:8000/api/v1"
TENANT_ID = "tenant-test-1"

async def main():
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Health Check
        print("1. Checking Health...")
        resp = await client.get("http://localhost:8000/health")
        print(f"   Status: {resp.status_code}, Body: {resp.json()}")

        # 2. Ingest Document
        print("\n2. Ingesting Document...")
        doc_data = {
            "title": "Distributed Systems Design",
            "content": "Distributed systems require careful consideration of consistency, availability, and partition tolerance."
        }
        headers = {"X-Tenant-ID": TENANT_ID}
        start = time.time()
        resp = await client.post(f"{BASE_URL}/documents/", json=doc_data, headers=headers)
        took = (time.time() - start) * 1000
        print(f"   Status: {resp.status_code}, Took: {took:.2f}ms")
        if resp.status_code != 200:
            print("   Failed to ingest")
            return
        doc_id = resp.json()["id"]
        print(f"   Doc ID: {doc_id}")

        # 3. Wait for Indexing (Eventual Consistency)
        print("\n3. Waiting 1s for consistency...")
        await asyncio.sleep(1)

        # 4. Search (First Hit - Should miss cache)
        print("\n4. Searching 'consistency' (Cache Miss)...")
        start = time.time()
        resp = await client.get(f"{BASE_URL}/documents/search", params={"q": "consistency"}, headers=headers)
        took = (time.time() - start) * 1000
        print(f"   Status: {resp.status_code}, Results: {len(resp.json())}, Took: {took:.2f}ms")

        # 5. Search (Second Hit - Should hit cache)
        print("\n5. Searching 'consistency' (Cache Hit)...")
        start = time.time()
        resp = await client.get(f"{BASE_URL}/documents/search", params={"q": "consistency"}, headers=headers)
        took = (time.time() - start) * 1000
        print(f"   Status: {resp.status_code}, Results: {len(resp.json())}, Took: {took:.2f}ms")
        
        # 6. Get Document
        print("\n6. Fetching single document...")
        resp = await client.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        print(f"   Status: {resp.status_code}")

        # 7. Delete Document
        print("\n7. Deleting document...")
        resp = await client.delete(f"{BASE_URL}/documents/{doc_id}", headers=headers)
        print(f"   Status: {resp.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
