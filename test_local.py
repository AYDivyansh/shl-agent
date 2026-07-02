"""
Quick local sanity check.
Run: python test_local.py
"""
import requests

BASE = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE}/health", timeout=10)
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
    print("✅ /health OK")

def test_vague_query():
    r = requests.post(f"{BASE}/chat", json={
        "messages": [{"role": "user", "content": "I need an assessment"}]
    }, timeout=30)
    data = r.json()
    print("Vague query response:", data)
    assert data["recommendations"] == [], "Should NOT recommend on vague query"
    assert "reply" in data and len(data["reply"]) > 0
    print("✅ Vague query handled correctly")

def test_off_topic():
    r = requests.post(f"{BASE}/chat", json={
        "messages": [{"role": "user", "content": "What's the best salary for a Java dev?"}]
    }, timeout=30)
    data = r.json()
    print("Off-topic response:", data)
    assert data["recommendations"] == []
    print("✅ Off-topic refused")

def test_full_flow():
    msgs = [
        {"role": "user", "content": "Hiring a Java developer who works with stakeholders"},
    ]
    r1 = requests.post(f"{BASE}/chat", json={"messages": msgs}, timeout=30).json()
    print("Turn 1:", r1)
    msgs.append({"role": "assistant", "content": r1["reply"]})
    msgs.append({"role": "user", "content": "Mid-level, around 4 years"})
    r2 = requests.post(f"{BASE}/chat", json={"messages": msgs}, timeout=30).json()
    print("Turn 2:", r2)
    assert len(r2["recommendations"]) >= 1
    assert len(r2["recommendations"]) <= 10
    print("✅ Full flow works")

if __name__ == "__main__":
    test_health()
    test_vague_query()
    test_off_topic()
    test_full_flow()
    print("\n🎉 All local tests passed")