"""Define functions to use in redis queue."""

import os
import time

from rq import get_current_job

from .database import firestore_client


def some_long_function(some_input):
    """An example function for redis queue."""
    job = get_current_job()
    time.sleep(10)

    doc_ref = firestore_client.collection(
        os.getenv("FIRESTORE_COLLECTION", "demo_collection")
    ).document(job.id)

    result = {
        "job_id": job.id,
        "job_enqueued_at": job.enqueued_at.isoformat(),
        "job_started_at": job.started_at.isoformat(),
        "input": some_input,
        "result": some_input,
    }

    doc_ref.set(result)

    return result
