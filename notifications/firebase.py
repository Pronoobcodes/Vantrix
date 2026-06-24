import firebase_admin

from firebase_admin import messaging, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate('notifications/firebase-service-account.json')
firebase_admin.initialize_app(cred)