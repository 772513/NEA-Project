from app import create_app

# create instance of Flask application
app = create_app()

# run app in development mode
if __name__ == "__main__":
    app.run(debug=True)