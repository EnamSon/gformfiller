# gformfiller/api/inscriptions.py

import logging
import time
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import (
    APIRouter, Request, HTTPException, Depends,
    Body, UploadFile, File, BackgroundTasks, Form
)

from .deps import get_current_user
from gformfiller.core.constants import Status
from gformfiller.infrastructure.folder_manager.constants import (
    FILES_SUBDIR,
    FileKeys,
    LOCK_FILE,
)

router = APIRouter(prefix="/gformfiller/inscriptions", tags=["Inscriptions"])
logger = logging.getLogger(__name__)


# --- routes spécifique au projet TCFFormFiller ---

@router.get("/", response_model=List[Dict[str, str]])
async def list_inscriptions(request: Request, current_user: str = Depends(get_current_user)):
    fm = request.app.state.folder_manager
    all_form_data = fm.get_all_form_data(current_user)
    all_metadata = fm.get_all_metadata(current_user)
    infos = []

    for filler_name in all_form_data:
        full_name = ""
        try:
            full_name = all_form_data[filler_name]["TextResponse"].get(
                "nom < complet", filler_name.replace("_", " ")
            )
        except Exception as e:
            logger.error(f"Can't extract the fullname for reason: {e}")
            continue

        phone = ""
        try:
            phone = all_form_data[filler_name]["TextResponse"].get("phone", "")
        except Exception as e:
            logger.error(f"Can't extract phone number for reason: {e}")
            continue

        status = all_metadata[filler_name].get("status", "unknown")
        date = all_metadata[filler_name].get("created_at", "")

        infos.append({
            "id": filler_name,
            "full_name": full_name,
            "phone": phone,
            "status": status,
            "date": date
        })

    return infos


@router.post("/register/")
async def register_candidate(
    request: Request,
    nom: str = Form(...),
    prenom: str = Form(...),
    ville: str = Form(...),
    nationalite: str = Form(...),
    pays: str = Form(...),
    email: str = Form(...),
    cni_number: str = Form(...),
    langue: str = Form(...),
    phone: str = Form(...),
    birthdate: str = Form(...),
    sexe: str = Form(...),
    photo: UploadFile = File(...),
    document: UploadFile = File(...),
    current_user:str = Depends(get_current_user)
):
    fm = request.app.state.folder_manager
    
    filler_name = f"cand_{uuid.uuid4().hex[:8]}"
    fm.create_filler(current_user, filler_name)

    filler_paths = fm.get_filler_paths(current_user, filler_name)
    files_dir = filler_paths[FILES_SUBDIR]
    photo_path = files_dir / photo.filename
    doc_path = files_dir / document.filename
    
    with open(photo_path, "wb") as f: f.write(await photo.read())
    with open(doc_path, "wb") as f: f.write(await document.read())

    form_data = {
        "TextResponse": {
            "nom < complet": f"{nom} {prenom}",
            "prénom | prenom": prenom,
            "nom": nom,
            "ville": ville,
            "nationalit": nationalite,
            "pays": pays,
            "motif": "Immigration Canada",
            "courriel | email | e-mail": email,
            "cni | passport | passeport": cni_number,
            "langue": langue,
            "phone": phone
        },
        "DateResponse": { "": birthdate },
        "CheckboxResponse": { "": "" },
        "RadioResponse": {
            "handicap | maladie": "aucun",
            "sexe | genre": sexe
        },
        "FileUploadResponse": {
            "photo": str(photo_path),
            "cni | (document < identification) | passport | passeport": str(doc_path)
        }
    }
    fm.update_filler_file_content(current_user, filler_name, FileKeys.FORMDATA, form_data)

    config_data = {
        "headless": True,
        "remote": False,
        "wait_time": 5.0,
        "submit": True
    }
    fm.update_filler_file_content(current_user, filler_name, FileKeys.CONFIG, config_data)

    return {
        "filler_name": filler_name,
    }


async def process_queue(
        request: Request, url: str,
        filler_names: List[str],
        current_user: str = Depends(get_current_user)
):
    fm = request.app.state.folder_manager
    worker = request.app.state.automation_worker
    
    # 1. Trier les fillers par date de création (created_at dans metadata)
    detailed_fillers = []
    for name in filler_names:
        meta = fm.get_filler_file_content(current_user, name, FileKeys.METADATA)
        detailed_fillers.append({"name": name, "created_at": meta.get("created_at", "")})
    
    # Tri ascendant (le plus ancien en premier)
    queue = sorted(detailed_fillers, key=lambda x: x["created_at"])
    
    while queue:
        # 2. Chercher un profil réellement libre
        all_profiles = fm.list_profiles()
        free_profile = None
        
        for p in all_profiles:
            lock_path = fm.profiles_dir / p / LOCK_FILE
            if not lock_path.exists():
                free_profile = p
                break
        
        if free_profile:
            candidate = queue.pop(0) # On récupère le plus ancien
            c_name = candidate["name"]
            
            # 3. Attribuer le profil et l'URL au dernier moment
            config = fm.get_filler_file_content(current_user, c_name, FileKeys.CONFIG)
            config["profile"] = free_profile
            fm.update_filler_file_content(current_user, c_name, FileKeys.CONFIG, config)
            
            meta = fm.get_filler_file_content(current_user, c_name, FileKeys.METADATA)
            meta["url"] = url
            fm.update_filler_file_content(current_user, c_name, FileKeys.METADATA, meta)

            # 4. Lancer le worker (le worker doit créer le .lock au début du run et le supprimer à la fin)
            # On utilise asyncio.to_thread pour ne pas bloquer la boucle d'événements
            asyncio.create_task(asyncio.to_thread(worker.run, user_id=current_user, filler_name=c_name))
            
            logger.info(f"Profil {free_profile} attribué à {c_name}. Reste en file : {len(queue)}")
            time.sleep(1.0)
        else:
            # Aucun profil libre, on attend 5 secondes avant de réessayer
            await asyncio.sleep(5)


@router.post("/run/")
async def run_inscriptions(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    filler_names: List[str] = Form(...),
    current_user: str = Depends(get_current_user)
):
    # On lance le gestionnaire de file d'attente en arrière-plan
    background_tasks.add_task(process_queue, request, url, filler_names, current_user)
    
    return {
        "message": f"File d'attente activée pour {len(filler_names)} fillers.",
        "status": "processing_queue"
    }


@router.get("/pending/count/", response_model=int)
async def pending_inscriptions_count(
    request: Request, current_user: str = Depends(get_current_user)
):
    fm = request.app.state.folder_manager
    all_metadata = fm.get_all_metadata(current_user)
    return sum(1 for filler_name in all_metadata if all_metadata[filler_name].get("status") == Status.PENDING)


@router.get("/status/", response_model=Dict[str, int])
async def status(request: Request, cuurent_user: str = Depends(get_current_user)):
    fm = request.app.state.folder_manager
    all_metadata = fm.get_all_metadata(cuurent_user)
    total = len(all_metadata)
    pending = 0
    failed = 0
    completed = 0
    for metadata in all_metadata.values():
        status = metadata.get("status")
        if status == Status.PENDING:
            pending += 1
        elif status == Status.COMPLETED:
            completed += 1
        else:
            failed += 1

    return {
        "total": total,
        Status.PENDING: pending,
        Status.FAILED: failed,
        Status.COMPLETED: completed
    }

# /gformfiller/inscriptions/pending_list
@router.get("/pending_list/", response_model=List[Dict[str, str]])
async def pending_list(
    request: Request, current_user: str = Depends(get_current_user)
):
    fm = request.app.state.folder_manager
    all_metadata = fm.get_all_metadata(current_user)
    fm = request.app.state.folder_manager
    all_form_data = fm.get_all_form_data(current_user)

    pending_list = []
    for filler_name in all_form_data:
        full_name = ""
        try:
            full_name = all_form_data[filler_name]["TextResponse"].get(
                "nom < complet", filler_name.replace("_", " ")
            )
        except Exception as e:
            logger.error(f"Can't extract the fullname for reason: {e}")

        phone = ""
        try:
            phone = all_form_data[filler_name]["TextResponse"].get("phone", "")
        except Exception as e:
            logger.error(f"Can't extract phone number for reason: {e}")

        status = all_metadata[filler_name].get("status", "unknown")
        date = all_metadata[filler_name].get("created_at", "")

        if status == "pending":
            pending_list.append({
                "id": filler_name,
                "full_name": full_name,
                "phone": phone,
                "status": status,
                "date": date
            })

    return pending_list


@router.get("/details/")
async def get_candidate_details(
    request: Request,
    filler_name: str,
    current_user: str = Depends(get_current_user)
):
    fm = request.app.state.folder_manager
    
    if filler_name not in fm.list_fillers(current_user):
        raise HTTPException(status_code=404, detail="Candidat non trouvé")
        
    try:
        # On récupère le formdata.json qui contient toutes les infos du register
        form_data = fm.get_filler_file_content(current_user, filler_name, FileKeys.FORMDATA)
        
        # On reconstruit l'objet plat pour le frontend (inversion du mapping)
        text_resp = form_data.get("TextResponse", {})
        radio_resp = form_data.get("RadioResponse", {})
        
        return {
            "nom": text_resp.get("nom"),
            "prenom": text_resp.get("prénom | prenom"),
            "ville": text_resp.get("ville"),
            "nationalite": text_resp.get("nationalit"),
            "pays": text_resp.get("pays"),
            "email": text_resp.get("courriel | email | e-mail"),
            "cni_number": text_resp.get("cni | passport | passeport"),
            "langue": text_resp.get("langue"),
            "phone": text_resp.get("phone"),
            "birthdate": form_data.get("DateResponse", {}).get(""),
            "sexe": radio_resp.get("sexe | genre"),
            # On renvoie les noms des fichiers pour le front
            # "photo_filename": os.path.basename(form_data.get("FileUploadResponse", {}).get("photo", "")),
            # "doc_filename": os.path.basename(form_data.get("FileUploadResponse", {}).get("cni | (document < identification) | passport | passeport", ""))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de lecture : {str(e)}")