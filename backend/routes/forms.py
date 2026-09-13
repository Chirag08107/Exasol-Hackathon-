from fastapi import APIRouter,HTTPException,status

from services.form_service import (
    get_all_forms,get_form_by_id,get_form_fields,
    get_form_requirements,
    get_form_documents,
    get_form_rules,
    get_form_mistakes,
    get_form_sources,
    search_forms as search_form_service
)

router = APIRouter(
    prefix="/api/forms",
    tags=["Forms"]
)


@router.get("/")
def get_forms():
    return get_all_forms()


@router.get("/search")
def search_forms(q: str):
    return {
        "query": q,
        "results":search_form_service(q)
    }


@router.get("/{form_id}")
def get_form(form_id: int):
    form = get_form_by_id(form_id)

    if form is None:
        return {
            "message": "Form not found"
        }

    return form 


@router.get("/{form_id}/fields")
def get_form_fields_route(form_id: int):
   form = get_form_by_id(form_id)

   if form is None:
       raise HTTPException(
           status_code = status.HTTP_404_NOT_FOUND,
           detail="Form not found"
       )
   return get_form_fields(form_id)


@router.get("/{form_id}/requirements")
def get_form_requirements_route(form_id: int):

    form = get_form_by_id(form_id)

    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return get_form_requirements(form_id)


@router.get("/{form_id}/documents")
def get_form_documents_route(form_id: int):

    form = get_form_by_id(form_id)

    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return get_form_documents(form_id)


@router.get("/{form_id}/rules")
def get_form_rules_route(form_id: int):

    form = get_form_by_id(form_id)

    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return get_form_rules(form_id)


@router.get("/{form_id}/mistakes")
def get_form_mistakes_route(form_id: int):

    form = get_form_by_id(form_id)

    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return get_form_mistakes(form_id)


@router.get("/{form_id}/sources")
def get_form_sources_route(form_id: int):

    form = get_form_by_id(form_id)

    if form is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form not found"
        )

    return get_form_sources(form_id)