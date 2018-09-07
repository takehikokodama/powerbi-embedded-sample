import os
import requests
import json
import logging

import adal
from sanic import Sanic
from sanic.response import html
from jinja2 import Environment, PackageLoader, select_autoescape

log = logging.getLogger()
app = Sanic(__name__)

# Load the template environment with async support
template_env = Environment(
    loader=PackageLoader("powerbi_embedded_sample", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)


def get_token(domain):
    context = adal.AuthenticationContext(
        os.environ["PBI_AUTHORITY"], validate_authority=True, api_version=None
    )

    token_response = context.acquire_token_with_username_password(
        os.environ["PBI_RESOURCE"],
        os.environ["PBI_USERNAME"],
        os.environ["PBI_PASSWORD"],
        os.environ["PBI_CLIENTID"],
    )
    aad_token = token_response["accessToken"]

    headers = {"Authorization": "Bearer " + aad_token}
    response = requests.get(
        "https://api.powerbi.com/v1.0/myorg/groups", headers=headers
    )

    # If PBI_WORKSPACE_NAME is set, get workspace with that name
    # If it is not set or no such workspace, get the first workspace
    bi_groups = json.loads(response.text)["value"]
    log.debug("group info:\n" + str(bi_groups))

    group_id = ""
    if "PBI_WORKSPACE_NAME" in os.environ:
        for gid in bi_groups:
            if gid["name"] == os.environ["PBI_WORKSPACE_NAME"]:
                group_id = gid["id"]

    if group_id == "":
        log.warn(
            "Workspace name is set but there is no such workspace: "
            + os.environ["PBI_WORKSPACE_NAME"]
        )
        group_id = bi_groups[0]["id"]

    response = requests.get(
        "https://api.powerbi.com/v1.0/myorg/groups/" + group_id + "/reports",
        headers=headers,
    )

    # Pick the 1st report in the App Workspace (aka group)
    bi_reports = json.loads(response.text)["value"]

    log.debug("Reports json:\n" + str(bi_reports))

    reportId = embedUrl = datasetID = ""
    if "PBI_REPORT_NAME" in os.environ:
        for rid in bi_reports:
            if rid["name"] == os.environ["PBI_REPORT_NAME"]:
                reportId = rid["id"]
                embedUrl = rid["embedUrl"]
                datasetID = rid["datasetId"]

    if reportId == "":
        log.warn(
            "Report name is set but there is no such report: "
            + os.environ["PBI_REPORT_NAME"]
        )
        reportId = bi_reports[0]["id"]
        embedUrl = bi_reports[0]["embedUrl"]

    post_data = {
        "accessLevel": "View",
        "identities": [
            {
                "username": domain,
                "roles": [os.environ["PBI_VIEW_ROLE"]],
                "datasets": [datasetID],
            }
        ],
    }

    headers.update({"Content-type": "application/json"})

    response = requests.post(
        "https://api.powerbi.com/v1.0/myorg/groups/"
        + group_id
        + "/reports/"
        + reportId
        + "/GenerateToken",
        data=json.dumps(post_data),
        headers=headers,
    )

    report_token = json.loads(response.text)["token"]

    return {"token": report_token, "url": embedUrl, "report_id": reportId}


async def handle_request_with_no_domain(request):
    if not request.cookies.get("user_id"):
        return html(
            """
            <li><a href="./tokyo.example.com">tokyo.example.com</a></li>
            <li><a href="./osaka.example.com">osaka.example.com</a></li>
            """
        )


async def index(request, path):
    template = template_env.get_template("index.html")
    config = get_token(path)
    content = template.render(config=json.dumps(config), domain=path)
    return html(content)


def main():
    log.setLevel(logging.getLevelName(os.environ.get("PBI_LOG_LEVEL", logging.WARNING)))
    app.add_route(handle_request_with_no_domain, "/")
    app.add_route(index, "/<path:[A-z0-9.]+>")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    static_directory = os.path.join(current_directory, "static")
    app.static("/static", static_directory)

    app.run(host="0.0.0.0", port="8000")


if __name__ == "__main__":
    main()
