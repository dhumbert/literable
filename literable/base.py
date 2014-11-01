from literable import app, model


app.jinja_env.globals['is_book_in_reading_list'] = model.is_book_in_reading_list


from literable.views import book
from literable.views import reading_list
from literable.views import admin
from literable.views import taxonomy
from literable.views import auth
from literable.views import search
