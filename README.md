A Flask-based backend system that enables users to create and manage events, collaborate via shared access, and maintain a full version history with rollback capabilities.

Features
1.User registration and login with JWT authentication

2.Event creation, editing, and deletion

3.Role-based access: Owner, Editor, Viewer

4.Share events with other users

5.Recurring event support

6.Versioning with rollback and changelog

Setup

1. Clone the repository and navigate into it:

   git clone https://github.com/mimansha19/Event-management.git
   
   cd event-management

3. Create and activate a virtual environment:
   
   python3 -m venv venv
   
   source venv/bin/activate

5. pip install -r requirements.txt

6. Initialize the database:
   flask db init
   
   flask db migrate -m "initial"
   
   flask db upgrade

8. Run the development server:
   python run.py
