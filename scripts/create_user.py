from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def create_user_with_metadata(
    email: str, password: str, display_name: str, other_metadata: dict = {}
):
    try:
        user = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
                "options": {
                    "data": {"display_name": display_name, **other_metadata},
                    "email_confirm": True,
                },
            }
        )

        if user.user is None:
            raise Exception("User creation failed")

        print(f"User created successfully. User ID: {user.user.id}")
        return user.user

    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None


if __name__ == "__main__":
    new_user = create_user_with_metadata(
        email="Jaen@example.com",
        password="securepassword123",
        display_name="Jaen",
    )

    if new_user:
        print(f"User created: {new_user.email}")
        print(f"Display Name: {new_user.user_metadata.get('display_name')}")
        print(f"Other Metadata: {new_user.user_metadata}")
