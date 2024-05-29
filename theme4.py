#Rémy Cuvelier - Mai 2023
#Script qui utilise une api http pour récupérer une liste d'utilisateurs a synchroniser avec les utilisateurs d'un active directory
import subprocess
import urllib.request
import json
id_sae=3
id_grp="b1"
login="cuvelire"
myUrl = f"http://srv-peda.iut-acy.local/hoarauju/sae204/users/apiUsers.php?id_sae={id_sae}&id_grp={id_grp}&login_usmb={login}"
def run(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed
def getData(url):
    with urllib.request.urlopen(myUrl) as url:
        data = json.loads(url.read().decode())
        return data
def viewUsers(data):
    for user in data:
        print(user)
def statUsers(data):
    #fonction qui retourne le nombre d'employés, le nombre de groupes et le nom de domaine
    #donne le nombre d'employé grace a la longueur du dictionnaire
    nbEmployes = len(data)
    nomGroupe=[]
    #ajout de chaque nom de groupe qui ne sont pas encore dans la liste "nomGroupe"
    for user in data:
        if user["groupe"] not in nomGroupe:
            nomGroupe.append(user["groupe"])
    #donne le nombre de groupe grace a la longueu de la liste
    nbGroupes = len(nomGroupe)
    #récupération de l'adresse mail du premier utilisateur pour ensuite déterminer le nom de domaine
    mailDomaine = data[0]["email"]
    #récupération du nom de domaine contenue dans les adresse mail (2ème partie de l'adresse mail après le @)
    nomDomaine = mailDomaine.split("@")[1]
    #renvoie les valeurs
    return(nbEmployes,nbGroupes,nomDomaine)
def createUsers(data):
    #fonction qui crée les utilisateurs dans l'active directory en utilisant les données de l'api via des commandes powershell
    for user in data:
        #vériication que l'utilisateur n'existe pas déjà
        command = "Get-ADUser -Identity "+user["login"]
        result = run(command)
        #test si l'utilisateur existe pas
        if result.returncode !=0:
            #si il existe pas on le créer
            #création des utilisateurs
            command = "New-ADUser -Name "+user["nom"]+" "+user["prenom"]+" -GivenName "+user["prenom"]+" -Surname "+user["nom"]+" -SamAccountName "+user["login"]+" -UserPrincipalName "+user["email"]+" -AccountPassword (ConvertTo-SecureString -AsPlainText "+user["password"]+" -Force) -Enabled $true -Path 'OU=SAE204,OU=SAE,DC="+user["email"].split("@")[1]+",DC=local'"
            print("user : ",user["nom"],user["prenom"],user["login"],user["email"] )
            result = run(command)
            #test si le groupe existe déja
            command= 'Get-ADGroup -Filter {Name -eq"'+user["groupe"]+'"}'
            result = run(command)
            #si le groupe n'existe pas on le créer
            if result.returncode!=0:
                command=f'New-ADGroup -Name {user["groupe"]} -SamAccountName {user["groupe"]} -GroupCategory Security -GroupScope Global'
                result=run(command)
            #ajout des utilisateurs dans les groupes
            command = "Add-ADGroupMember -Identity "+user["groupe"]+" -Members "+user["login"]
            result = run(command)
            print(f'utilisateur {user["nom"]} {user["prenom"]} créer avec succès, il appartient au groupe {user["groupe"]}')
        else:
            print(f'Utilisateur {user["nom"]} {user["prenom"]} déja existant')


#-----------------------------------------------------------------------------------------------------------------------------
#Programme Principal
#-----------------------------------------------------------------------------------------------------------------------------
users=getData(myUrl)
viewUsers(users)
nbE,nbG,nomD=statUsers(users)
print(f"Vous allez importer {nbE} utilisateurs, répartis en {nbG} groupes et avec comme nom de domaine {nomD}")
continuer=input("voulez vous continuer ? y/N ")
if continuer=="y" or continuer=="Y":
    createUsers(users)
else:
    print("Création abandonnée")
