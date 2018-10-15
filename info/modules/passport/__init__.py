from flask import Blueprint

passport_blue = Blueprint("image_code",__name__,url_prefix="/passport")

from . import views