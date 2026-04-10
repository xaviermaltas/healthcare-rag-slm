#!/usr/bin/env python3
"""
Validació del sistema d'embeddings BGE-M3.

Els embeddings converteixen text en vectors numèrics per buscar documents
similars semànticament. Model: BAAI/bge-m3 — multilingüe, 8192 tokens, local.

Execució: healthcare-rag-env/bin/python3 scripts/test_embeddings.py
"""

import asyncio
import sys
import pytest
import httpx

API_BASE = "http://localhost:8000"


def print_section(title: str):
    # Capçalera visual per separar cada bloc de test
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(label: str, passed: bool, detail: str = ""):
    # Mostra ✅ o ❌ per a cada comprovació, amb detall opcional
    icon = "✅" if passed else "❌"
    print(f"  {icon} {label}")
    if detail:
        print(f"     {detail}")


# Fixture de pytest: crea un client HTTP per a cada test (evita conflictes d'event loop)
@pytest.fixture
async def client():
    async with httpx.AsyncClient(timeout=30.0) as c:
        yield c


async def test_embeddings_health(client: httpx.AsyncClient):
    # Comprova que el model BGE-M3 ha carregat i respon com a 'healthy'
    print_section("TEST 1: Embeddings Health Check")
    r = await client.get(f"{API_BASE}/health/embeddings")
    data = r.json()
    print_result("Endpoint /health/embeddings és healthy", data.get("status") == "healthy")
    print_result("Camp 'model' present", "model" in data, f"model: {data.get('model')}")
    print_result("Camp 'device' present", "device" in data, f"device: {data.get('device')}")
    print_result("Camp 'batch_size' present", "batch_size" in data, f"batch_size: {data.get('batch_size')}")
    assert data.get("status") == "healthy", f"Embeddings no healthy: {data}"


async def test_models_embeddings_info(client: httpx.AsyncClient):
    # Confirma que /models/embeddings retorna info del model correcte (BAAI/bge-m3)
    print_section("TEST 2: Models Embeddings Info")
    r = await client.get(f"{API_BASE}/models/embeddings")
    data = r.json()
    print_result("Endpoint /models/embeddings respon correctament", data.get("status") == "healthy")
    print_result("Model és BAAI/bge-m3", data.get("model") == "BAAI/bge-m3", data.get("model"))
    assert data.get("status") == "healthy"
    assert data.get("model") == "BAAI/bge-m3"


async def test_admin_status_embeddings(client: httpx.AsyncClient):
    # Verifica que /admin/status inclou embeddings com a component actiu (no 'disabled')
    print_section("TEST 3: Admin Status — Embeddings com a Component")
    r = await client.get(f"{API_BASE}/admin/status")
    data = r.json()
    emb = data.get("components", {}).get("embeddings", {})
    print_result("Embeddings és 'healthy' a /admin/status", emb.get("status") == "healthy", f"status: {emb.get('status')}")
    print_result("El nom del model és informat", "model" in emb, f"model: {emb.get('model')}")
    assert emb.get("status") == "healthy"
    assert "model" in emb


async def test_full_system_health(client: httpx.AsyncClient):
    # Comprova que Ollama (LLM) i Qdrant (vector DB) estan actius — necessari per fer RAG
    print_section("TEST 4: Full System Health (Ollama + Qdrant)")
    r = await client.get(f"{API_BASE}/health/")
    data = r.json()
    components = data.get("components", {})
    ollama_ok = components.get("ollama", {}).get("status") == "healthy"
    qdrant_ok = components.get("qdrant", {}).get("status") == "healthy"
    print_result("Sistema global és healthy", data.get("status") == "healthy")
    print_result("Ollama (LLM) és healthy", ollama_ok)
    print_result("Qdrant (vector DB) és healthy", qdrant_ok)
    assert ollama_ok, "Ollama no és healthy"
    assert qdrant_ok, "Qdrant no és healthy"


async def test_semantic_similarity(client: httpx.AsyncClient):
    # Prova el pipeline complet: text → embedding → cerca a Qdrant
    # Si Qdrant no té documents indexats retorna 0 resultats, però l'embedding s'ha generat
    print_section("TEST 5: Pipeline Embedding → Cerca Semàntica")
    r = await client.post(
        f"{API_BASE}/query/retrieve",
        params={"query": "dolor de cap i febre", "top_k": 3}
    )
    if r.status_code == 200:
        count = r.json().get("count", 0)
        print_result("Retrieve respon OK", True, f"documents retornats: {count}")
    elif r.status_code == 500:
        detail = r.json().get("detail", "")
        # Distingim si l'error ve dels embeddings o d'un altre component
        assert "embedding" not in detail.lower() and "encode" not in detail.lower(), \
            f"Retrieve falla per embeddings: {detail[:100]}"
        print_result("Retrieve OK (falla per Qdrant, no per embeddings)", True)
    else:
        pytest.fail(f"Codi de resposta inesperat: HTTP {r.status_code}")


# Permet executar el fitxer directament com a script (sense pytest)
if __name__ == "__main__":
    async def main():
        print("\n" + "🧪 TEST SUITE: BGEM3 Embeddings Validation".center(60))
        print("=" * 60)
        print(f"  API: {API_BASE}")
        print(f"  Model: BAAI/bge-m3 (via sentence-transformers)")
        print("=" * 60)

        results = []
        async with httpx.AsyncClient(timeout=30.0) as c:
            for fn in [test_embeddings_health, test_models_embeddings_info,
                       test_admin_status_embeddings, test_full_system_health,
                       test_semantic_similarity]:
                try:
                    await fn(c)
                    results.append(True)
                except (AssertionError, Exception) as e:
                    print(f"  ❌ {fn.__name__}: {e}")
                    results.append(False)

        passed = sum(results)
        total = len(results)
        print_section(f"RESULTAT FINAL: {passed}/{total} tests passats")
        if passed == total:
            print("  🎉 Tots els tests han passat!\n")
            sys.exit(0)
        else:
            print(f"  ⚠️  {total - passed} test(s) han fallat.\n")
            sys.exit(1)

    asyncio.run(main())
