import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from .rag_core import get_mongo_collection, answer_question
from .agent import run_agent
from .tasks import ingest_document_task


@csrf_exempt
def create_document(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    text = data.get("text")
    if not text:
        return HttpResponseBadRequest("Campo 'text' é obrigatório")

    coll = get_mongo_collection()
    result = coll.insert_one({"text": text, "status": "pending"})
    doc_id = str(result.inserted_id)

    # dispara task de ingestão
    ingest_document_task.delay(doc_id)

    return JsonResponse({"doc_id": doc_id, "status": "pending"})


@csrf_exempt
def ask(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    question = data.get("question")
    if not question:
        return HttpResponseBadRequest("Campo 'question' é obrigatório")

    result = answer_question(question)
    return JsonResponse(result)


@csrf_exempt
def agent_endpoint(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Use POST")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("JSON inválido")

    goal = data.get("goal")
    if not goal:
        return HttpResponseBadRequest("Campo 'goal' é obrigatório")

    answer = run_agent(goal)
    return JsonResponse({"result": answer})
