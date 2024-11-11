from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token, fake
from core.environment.host import get_host_for_locust_testing


class DepositionBehavior(TaskSet):
    def on_start(self):
        # Optional: login or setup preconditions here
        pass

    @task
    def create_deposition(self):
        response = self.client.get("/depositions/create")  # Adjust URL as needed
        csrf_token = get_csrf_token(response)
        
        # Payload for creating a new deposition
        response = self.client.post("/depositions/create", data={
            "title": fake.sentence(nb_words=6),
            "description": fake.text(),
            "upload_type": "dataset",
            "publication_type": "publication",
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Deposition creation failed: {response.status_code}")

    @task
    def get_deposition(self):
        # Assuming an endpoint for retrieving deposition details
        deposition_id = 1  # Replace with logic to get a real ID if necessary
        response = self.client.get(f"/depositions/{deposition_id}")
        if response.status_code != 200:
            print(f"Failed to retrieve deposition {deposition_id}: {response.status_code}")


class FakenodoUser(HttpUser):
    tasks = [DepositionBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()