"""The Flask App."""

# pylint: disable=broad-except

import time

from flask import Flask, _app_ctx_stack, abort, jsonify, request
from rq.job import Job
from sqlalchemy.orm import scoped_session

from . import models
from .database import SessionLocal, engine
from .functions import some_long_function
from .redis_resc import redis_conn, redis_queue

models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.db = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)


@app.errorhandler(404)
def resource_not_found(exception):
    """Returns exceptions as part of a json."""
    return jsonify(error=str(exception)), 404


@app.route("/")
def home():
    """Show the app is working."""
    return "Running!"


@app.route("/enqueue")
def enqueue():
    """Enqueues a task into redis queue to be processes.
    Returns the job_id."""
    job = redis_queue.enqueue(
        some_long_function, f"This message was queued it {time.time()}"
    )
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
    except Exception as exception:
        abort(404, description=exception)

    if not job.result:
        abort(
            404,
            description=f"No result found for job_id {job.id}. Try checking the job's status.",
        )
    return jsonify(job.result)


@app.route("/get_result_from_database")
def get_result_from_database():
    """Takes a job_id and returns the job's result from the SQL database."""
    job_id = request.args["job_id"]

    try:
        result = (
            app.db.query(models.Result).filter(models.Result.job_id == job_id).first()
        )
        return result.to_dict()
    except Exception as exception:
        abort(404, description=exception)


@app.teardown_appcontext
def remove_session(*args, **kwargs):  # pylint: disable=unused-argument
    """Closes the database session."""
    app.db.remove()


if __name__ == "__main__":
    app.run(debug=True)
