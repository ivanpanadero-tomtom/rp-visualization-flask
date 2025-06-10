#!/usr/bin/env bash
set -euo pipefail

# ----- configure these -----
SUBSCRIPTION="07c2abb3-4071-4c2a-976d-ec1f8002ad64"
RG="rg-sv-cimain-mapsanalytics-dev"
CG="ci-sv-poisrpvisual-mapsanalytics-dev"

DNS_RG="my-dns-resource-group"
ZONE="example.com"
RECORD="app"
# ----------------------------

# Get the current IP
IP=$(az container show \
  --subscription "$SUBSCRIPTION" \
  --resource-group "$RG" \
  --name "$CG" \
  --query "ipAddress.ip" -o tsv)

# Update (or create) the A record
az network dns record-set a add-record \
  --resource-group "$DNS_RG" \
  --zone-name "$ZONE" \
  --record-set-name "$RECORD" \
  --ipv4-address "$IP" \
  --ttl 300

echo "✅ Updated DNS: $RECORD.$ZONE → $IP"
