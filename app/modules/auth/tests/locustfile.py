from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token, fake
from core.environment.host import get_host_for_locust_testing


class SignupBehavior(TaskSet):
    def on_start(self):
        self.signup()

    @task
    def signup(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "email": fake.email(),
            "password": fake.password(),
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")


class LoginBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": 'user1@example.com',
            "password": '1234',
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class AuthUser(HttpUser):
    tasks = [SignupBehavior, LoginBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()

class ExtendedSignupBehavior(SignupBehavior):

    @task
    def signup_initial_email_not_confirmed(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "name": "Test",
            "surname": "User",
            "email": "unconfirmed@example.com",
            "password": "password123",
            "csrf_token": csrf_token
        }, allow_redirects=True)

        if response.status_code == 200 and "/confirm-email" in response.url:
            print("Signup initial email not confirmed - Passed")
        else:
            print("Signup initial email not confirmed - Failed")

    @task
    def signup_redirects_to_email_confirmation(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "name": "Test",
            "surname": "User",
            "email": "redirect_confirm@example.com",
            "password": "password123",
            "csrf_token": csrf_token
        }, allow_redirects=True)

        if response.status_code == 200 and "/confirm-email" in response.url:
            print("Signup redirects to email confirmation - Passed")
        else:
            print("Signup redirects to email confirmation - Failed")


class ExtendedLoginBehavior(LoginBehavior):

    @task
    def login_fails_for_unconfirmed_user(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": "unconfirmed_login@example.com",
            "password": "password123",
            "csrf_token": csrf_token
        }, allow_redirects=True)

        if response.status_code == 200 and "/confirm-email" in response.url:
            print("Login fails for unconfirmed user - Passed")
        else:
            print("Login fails for unconfirmed user - Failed")

    @task
    def login_succeeds_after_confirmation(self):
        response = self.client.get("/login")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/login", data={
            "email": "confirmed_user@example.com",
            "password": "password123",
            "csrf_token": csrf_token
        }, allow_redirects=True)

        if response.status_code == 200 and "/public/index" in response.url:
            print("Login succeeds after confirmation - Passed")
        else:
            print("Login succeeds after confirmation - Failed")
