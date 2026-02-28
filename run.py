from app import create_app

# Create Flask app
app = create_app()
FLASK_PORT = 5000

if __name__ == '__main__': 
    app.run(debug=True)