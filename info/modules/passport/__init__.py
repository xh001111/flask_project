from flask import Blueprint

image_code = Blueprint("image_code",__name__,url_prefix="/passport")

from . import views