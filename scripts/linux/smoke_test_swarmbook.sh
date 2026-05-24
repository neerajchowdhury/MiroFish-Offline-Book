#!/usr/bin/env bash
# ============================================================================
# MiroFish-Offline — Smoke Test (Linux/macOS)
# ============================================================================
# Runs a minimal local-first flow against the backend.
#
# Usage:
#   bash scripts/linux/smoke_test_swarmbook.sh [http://localhost:5001]
# ============================================================================

set -euo pipefail

BACKEND_URL="${1:-http://localhost:5001}"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'

section() { echo -e "\n${CYAN}$(printf -- '-%.0s' {1..78})${NC}"; echo -e "${CYAN}$1${NC}"; echo -e "${CYAN}$(printf -- '-%.0s' {1..78})${NC}"; }
ok()    { echo -e "  ${GREEN}[OK]${NC} $1"; }
fail()  { echo -e "  ${RED}[FAIL]${NC} $1"; exit 1; }

section "MiroFish-Offline Smoke Test"
echo "  Backend: $BACKEND_URL"

section "1) Health"
RESP=$(curl -sf "$BACKEND_URL/api/book-sim/health" || echo "")
if [[ -z "$RESP" ]]; then fail "Health endpoint unreachable"; fi
ok "Health OK"

section "2) Create Project"
PROJECT=$(curl -sf -X POST "$BACKEND_URL/api/book-sim/projects" \
    -H "Content-Type: application/json" \
    -d '{"name":"Smoke Test","privacy_mode":"local_only","draft_id":"draft_smoke","version":"v1","metadata":{"local_profile":"local_tiny"}}' || echo "")
if [[ -z "$PROJECT" ]] || ! echo "$PROJECT" | grep -q '"success":true'; then
    fail "Project create failed: $PROJECT"
fi
PROJECT_ID=$(echo "$PROJECT" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['project_id'])" 2>/dev/null || echo "")
ok "Project OK: $PROJECT_ID"

section "3) Create Evidence Pack"
EVIDENCE=$(curl -sf -X POST "$BACKEND_URL/api/book-sim/evidence-packs" \
    -H "Content-Type: application/json" \
    -d "{\"project_id\":\"$PROJECT_ID\",\"title\":\"Smoke Draft\",\"author_name\":\"Tester\",\"text\":\"Chapter 1\\nMara gets a letter that threatens her promotion.\\n\\nChapter 2\\nAt the town hall, she realizes her mentor has been hiding the truth.\\n\\nChapter 3\\nShe must choose: protect the mentor or expose the truth.\"}" || echo "")
if [[ -z "$EVIDENCE" ]] || ! echo "$EVIDENCE" | grep -q '"success":true'; then
    fail "Evidence pack failed: $EVIDENCE"
fi
PACK_ID=$(echo "$EVIDENCE" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['evidence_pack']['pack_id'])" 2>/dev/null || echo "")
ok "Evidence pack OK: $PACK_ID"

section "4) Simulate"
SIM=$(curl -sf -X POST "$BACKEND_URL/api/book-sim/simulate" \
    -H "Content-Type: application/json" \
    -d "{\"project_id\":\"$PROJECT_ID\",\"evidence_pack_id\":\"$PACK_ID\",\"profile_name\":\"local_tiny\",\"privacy_mode\":\"local_only\",\"simulation_seed\":17}" || echo "")
if [[ -z "$SIM" ]] || ! echo "$SIM" | grep -q '"success":true'; then
    fail "Simulate failed: $SIM"
fi
ROUTE=$(echo "$SIM" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['route_selection']['selected_route'])" 2>/dev/null || echo "unknown")
ok "Sim OK. Selected route: $ROUTE"

PERSONA_ID=$(echo "$SIM" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['simulation_run']['reader_personas'][0]['persona_id'])" 2>/dev/null || echo "")
ok "Persona sample: $PERSONA_ID"

section "5) Persona Chat"
CHAT=$(curl -sf -X POST "$BACKEND_URL/api/book-sim/personas/$PERSONA_ID/chat" \
    -H "Content-Type: application/json" \
    -d "{\"project_id\":\"$PROJECT_ID\",\"question\":\"Why did you rate this book this way?\"}" || echo "")
if [[ -z "$CHAT" ]] || ! echo "$CHAT" | grep -q '"success":true'; then
    fail "Chat failed: $CHAT"
fi
ok "Chat OK"

section "Done"
echo -e "  ${GREEN}MiroFish-Offline smoke test completed successfully.${NC}"
