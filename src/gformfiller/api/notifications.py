# gformfiller/api/notifications

from gformfiller.infrastructure.folder_manager.constants import RECORD_SUBDIR
from .deps import get_current_user
from fastapi.responses import FileResponse, JSONResponse
from fastapi import (
    APIRouter, Request, HTTPException, Depends,
    Body, UploadFile, File, BackgroundTasks, Form
)
import os
import shutil
import tempfile
import logging


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gformfiller/notifications", tags=["Notifications"])


@router.get("/")
async def get_notifications_list(
    request: Request,
    base_id: int = 0,
    current_user = Depends(get_current_user)
):
    nm = request.app.state.notif_manager
    
    # 1. Récupération des données brutes de la DB
    raw_notifs = nm.get_notifications(current_user, last_id=base_id)

    enriched_notifications = []
    
    for n in raw_notifs:
        status = n["status"]
        f_name = n["filler_name"]
        
        # 2. Génération dynamique du titre et du message
        if status == "completed":
            title = "Inscription Réussie"
            message = f"Le remplissage pour {f_name} s'est terminé avec succès. Les enregistrements sont disponibles."
        elif status == "error":
            title = "Échec de l'automatisation"
            message = f"Une erreur est survenue lors du traitement de {f_name}."
        elif status == "pending":
            title = "Traitement en cours"
            message = f"Le profil Chrome travaille actuellement sur le dossier {f_name}."
        elif status == "failed":
            title = "Inscription échouée"
            message = f"La soumission du formulaire pour {f_name} a échouée."
        else:
            title = "Mise à jour système"
            message = f"Statut actuel pour {f_name} : {status}"

        # 3. Construction du JSON final
        enriched_notifications.append({
            "id": n["id"],
            "filler_name": f_name,
            "status": status,
            "created_at": n["created_at"],
            "title": title,
            "message": message
        })
        
    return enriched_notifications

@router.get("/details/")
async def get_notif_details(
    request: Request,
    id: int,
    current_user: str = Depends(get_current_user)
):
    nm = request.app.state.notif_manager
    fm = request.app.state.folder_manager
    
    notif = nm.get_notif_by_id(current_user, id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")

    filler_name = notif["filler_name"]
    filler_paths = fm.get_filler_paths(current_user, filler_name)
    filler_dir = filler_paths["root"]

    if not filler_dir.exists():
        raise HTTPException(status_code=404, detail="Dossier du candidat introuvable sur le disque")

    record_dir = filler_paths[RECORD_SUBDIR]

    if not record_dir.exists() or not any(record_dir.rglob('*')):
        return {
            "filler_name": filler_name,
            "message": "Aucun enregistrement effectué"
        }

    # Création d'un fichier temporaire pour le ZIP
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_zip_path = temp_zip.name
    temp_zip.close() # On ferme pour que shutil puisse écrire dedans

    try:
        # On compresse le dossier 'record'
        # base_name sans l'extension .zip car make_archive l'ajoute
        archive_base = temp_zip_path.replace(".zip", "")
        shutil.make_archive(archive_base, 'zip', record_dir)
        
        # 4. Envoi du fichier ZIP
        return FileResponse(
            path=temp_zip_path, 
            filename=f"records_{filler_name}.zip", 
            media_type='application/zip'
        )
    except Exception as e:
        logger.error(f"Erreur lors de la création du ZIP pour {filler_name}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération de l'archive.")