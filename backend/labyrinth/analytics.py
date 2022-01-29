import hashlib

from flask import Blueprint, request

import labyrinth.event_logging as logging

API = Blueprint("analytics", __name__, url_prefix='/analytics')

@API.route("/launch", methods=["POST"])
def app_launch():
    user_agent = request.user_agent.string.encode('utf-8')
    user_agent_hash = hashlib.md5(user_agent, usedforsecurity=False).hexdigest()
    logging.get_logger().app_launch(user_agent_hash)
    return ""
