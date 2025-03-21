import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app
from app.models import User, Match

# create instance of Flask application
app = create_app()


# run app in development mode
if __name__ == "__main__":
    app.run(debug=True)
