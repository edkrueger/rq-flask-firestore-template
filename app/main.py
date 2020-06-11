"""The Flask App."""

# pylint: disable=broad-except

import os

from flask import Flask, abort, jsonify, request
from rq.job import Job

from .database import firestore_client
from .functions import some_long_function
from .redis_resc import redis_conn, redis_queue

app = Flask(__name__)


@app.errorhandler(404)
def resource_not_found(exception):
    """Returns exceptions as part of a json."""
    return jsonify(error=str(exception)), 404


@app.route("/")
def home():
    """Show the app is working."""
    return "Running!"


@app.route("/enqueue", methods=["POST", "GET"])
def enqueue():
    """Enqueues a task into redis queue to be processes.
    Returns the job_id."""
    if request.method == "GET":
        query_param = request.args.get("external_id")
        if not query_param:
            abort(
                404,
                description=(
                    "No query parameter external_id passed. "
                    "Send a value to the external_id query parameter."
                ),
            )
        data = {"external_id": query_param}
    if request.method == "POST":
        data = request.json

    job = redis_queue.enqueue(some_long_function, data)
    return jsonify({"job_id": job.id})


@app.route("/check_status")
def check_status():
    """Takes a job_id and checks its status in redis queue."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exception:
        abort(404, description=exception)

    return jsonify({"job_id": job.id, "job_status": job.get_status()})


@app.route("/get_result")
def get_result():
    """Takes a job_id and returns the job's result."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)

        if not job.result:
            abort(
                404,
                description=f"No result found for job_id {job.id}. Try checking the job's status.",
            )

        return jsonify(job.result)

    except Exception as exception:
        abort(404, description=exception)


@app.route("/get_result_from_database")
def get_result_from_database():
    """Takes a job_id and returns the job's result from the SQL database."""
    job_id = request.args["job_id"]

    try:

        doc_ref = firestore_client.collection(
            os.getenv("FIRESTORE_COLLECTION", "demo_collection")
        ).document(job_id)

        doc = doc_ref.get()
        if not doc.exists:
            abort(
                404,
                f"No document found for job_id {job_id}. Try checking the job's status.",
            )

        return doc.to_dict()

    except Exception as exception:
        abort(404, description=exception)
