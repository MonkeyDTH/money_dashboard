from fastapi.templating import Jinja2Templates
from app.utils.template_filters import register_filters

templates = Jinja2Templates(directory="templates")
register_filters(templates)
