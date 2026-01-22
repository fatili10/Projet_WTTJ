# #!/bin/bash

# # -------------------------
# # CONFIGURATION VARIABLES
# # -------------------------
# RESOURCE_GROUP="RG_FELJATTIOUI"
# LOCATION="francecentral"
# STORAGE_ACCOUNT="adlseljattioui"
# CONTAINER_NAME="wttj"
# CSV_FILE="data/data.csv"
#   # Chemin vers ton CSV généré

# # -------------------------
# # AZ LOGIN
# # -------------------------
# echo " Connexion à Azure..."
# az login --only-show-errors

# # # -------------------------
# # # RESOURCE GROUP
# # # -------------------------
# # echo " Création du groupe de ressources : $RESOURCE_GROUP"
# # az group create \
# #   --name $RESOURCE_GROUP \
# #   --location $LOCATION

# # # -------------------------
# # # STORAGE ACCOUNT
# # # -------------------------
# # echo "Création du compte de stockage : $STORAGE_ACCOUNT"
# # az storage account create \
# #   --name $STORAGE_ACCOUNT \
# #   --resource-group $RESOURCE_GROUP \
# #   --location $LOCATION \
# #   --sku Standard_LRS \
# #   --kind StorageV2 \
# #   --hierarchical-namespace true

# # # -------------------------
# # # CONTAINER
# # # -------------------------
# # echo " Création du container : $CONTAINER_NAME"
# # az storage container create \
# #   --account-name $STORAGE_ACCOUNT \
# #   --name $CONTAINER_NAME \
# #   --auth-mode login

# # -------------------------
# # UPLOAD
# # -------------------------
# echo "⬆Upload du fichier CSV : $CSV_FILE"
# az storage blob upload \
#   --account-name $STORAGE_ACCOUNT \
#   --container-name $CONTAINER_NAME \
#   --name "$(basename $CSV_FILE)" \
#   --type block \
#   --file "$CSV_FILE" \
#   --auth-mode login \
#   --overwrite

# echo " Fichier téléversé avec succès dans Azure Data Lake Gen2 !"
# #!/bin/bash

# # -------------------------
# # CONFIGURATION VARIABLES
# # -------------------------
# RESOURCE_GROUP="RG_FELJATTIOUI"
# LOCATION="francecentral"
# STORAGE_ACCOUNT="adlseljattioui"
# CONTAINER_NAME="wttj"
# CSV_FILE="data/data.csv"

# # -------------------------
# # AZ LOGIN
# # -------------------------
# echo "🔐 Connexion à Azure..."
# az login --only-show-errors

# # -------------------------
# # CHECK CONTAINER
# # -------------------------
# echo "🔍 Vérification du conteneur..."
# az storage fs show \
#   --account-name $STORAGE_ACCOUNT \
#   --name $CONTAINER_NAME \
#   --auth-mode login >/dev/null 2>&1

# if [ $? -ne 0 ]; then
#   echo "📦 Conteneur inexistant, création..."
#   az storage fs create \
#     --account-name $STORAGE_ACCOUNT \
#     --name $CONTAINER_NAME \
#     --auth-mode login
# fi

# # -------------------------
# # UPLOAD (Data Lake Gen2)
# # -------------------------
# echo "⬆ Upload du fichier CSV : $CSV_FILE"
# az storage fs file upload \
#   --account-name $STORAGE_ACCOUNT \
#   --file-system $CONTAINER_NAME \
#   --path "$(basename $CSV_FILE)" \
#   --source "$CSV_FILE" \
#   --auth-mode login \
#   --overwrite

# echo "✅ Fichier téléversé avec succès dans Azure Data Lake Gen2 !"
#!/bin/bash

# -------------------------
# CONFIGURATION VARIABLES
# -------------------------

# -------------------------
# UPLOAD VIA ACCOUNT KEY
# -------------------------
#!/bin/bash

# Charger les variables .env
load_env

echo "⬆️ Upload du fichier CSV vers Azure Data Lake..."

az storage blob upload \
  --account-name $STORAGE_ACCOUNT \
  --account-key "$ACCOUNT_KEY" \
  --container-name $CONTAINER_NAME \
  --name "$(basename $CSV_FILE)" \
  --type block \
  --file "$CSV_FILE" \
  --overwrite

echo "✅ Fichier téléversé avec succès dans Azure Data Lake Gen2 !"
