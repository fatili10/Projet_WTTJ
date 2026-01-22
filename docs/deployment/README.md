  # 1. Copier le fichier exemple                                                                                                                                             
  cp terraform.tfvars.example terraform.tfvars                                                                                                                               
                                                                                                                                                                             
  # 2. Modifier les valeurs (surtout les noms qui doivent être uniques)                                                                                                      
  # IMPORTANT: Changer le mot de passe SQL !                                                                                                                                 
                                                                                                                                                                             
  # 3. Se connecter au nouveau tenant                                                                                                                                        
  az login --tenant <NOUVEAU_TENANT_ID>                                                                                                                                      
  az account set --subscription <NOUVELLE_SUBSCRIPTION_ID>                                                                                                                   
                                                                                                                                                                             
  # 4. Déployer                                                                                                                                                              
  terraform init                                                                                                                                                             
  terraform plan                                                                                                                                                             
  terraform apply                                                                                                                                                            
                                                                                                                                                                             
  Souhaites-tu que je modifie quelque chose ou que j'ajoute des ressources supplémentaires?                                                                                  
                                                                                              