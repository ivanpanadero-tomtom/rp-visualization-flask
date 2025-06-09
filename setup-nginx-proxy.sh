#!/bin/bash

# SETTINGS — update these if needed
RESOURCE_GROUP="rg-sv-cimain-mapsanalytics-dev"
VNET_NAME="myVNet"
SUBNET_NAME="mySubnet-vm"
VM_NAME="nginx-proxy-vm"
LB_NAME="lb-pois-visual"
LB_BACKEND_POOL="lb-backend-pool"
ACI_PRIVATE_IP="10.0.0.4"  # your ACI private IP
LOCATION="westeurope"

# ---- VM IMAGE FIX ----
VM_IMAGE="Ubuntu2204"  # valid image alias

echo "===== STEP 1: Creating VM in VNet ====="
az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image $VM_IMAGE \
  --size Standard_B1s \
  --admin-username azureuser \
  --generate-ssh-keys \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME

if [ $? -ne 0 ]; then
  echo "❌ ERROR: VM creation failed. Exiting."
  exit 1
fi

echo "===== STEP 2: Waiting for VM to be ready... ====="
az vm wait --created --name $VM_NAME --resource-group $RESOURCE_GROUP

echo "===== STEP 3: Installing NGINX and configuring reverse proxy... ====="
az vm extension set \
  --resource-group $RESOURCE_GROUP \
  --vm-name $VM_NAME \
  --name customScript \
  --publisher Microsoft.Azure.Extensions \
  --settings "{
    \"commandToExecute\": \"sudo apt update && sudo apt install -y nginx && echo 'server { listen 80; location / { proxy_pass http://$ACI_PRIVATE_IP; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; } }' | sudo tee /etc/nginx/sites-available/default > /dev/null && sudo nginx -t && sudo systemctl restart nginx\"
  }"

if [ $? -ne 0 ]; then
  echo "❌ ERROR: NGINX installation/configuration failed. Exiting."
  exit 1
fi

echo "===== STEP 4: Getting NIC name of VM... ====="
NIC_NAME=$(az vm show --name $VM_NAME --resource-group $RESOURCE_GROUP --query 'networkProfile.networkInterfaces[0].id' -o tsv | awk -F/ '{print $NF}')
echo "NIC_NAME = $NIC_NAME"

echo "===== STEP 5: Attaching NIC to LB backend pool... ====="
az network nic ip-config address-pool add \
  --address-pool $LB_BACKEND_POOL \
  --ip-config-name ipconfig1 \
  --nic-name $NIC_NAME \
  --resource-group $RESOURCE_GROUP \
  --lb-name $LB_NAME

if [ $? -ne 0 ]; then
  echo "❌ ERROR: Failed to attach NIC to LB backend pool. Exiting."
  exit 1
fi

echo "===== ✅ Setup complete! ====="
echo "👉 Your app should now be reachable at: http://4.180.88.99"

