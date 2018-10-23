from flask import Blueprint, request, redirect, session

admin_blue = Blueprint("admin_blue",__name__,url_prefix="/admin")

from . import views

@admin_blue.before_request
def visit_admin():
    if not request.url.endswith("admin/login"):
        if not session.get("is_admin"):
            return redirect("/")

