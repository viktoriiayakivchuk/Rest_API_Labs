from locust import HttpUser, task, between
import uuid

class BookLoadTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.username = f"u_{uuid.uuid4().hex[:8]}"
        self.password = "pass12345"
        self.email = f"{self.username}@example.com"
        
        self.client.post("/api/auth/register", json={
            "email": self.email,
            "username": self.username,
            "password": self.password
        })
        
        response = self.client.post("/api/auth/login", data={
            "username": self.username,
            "password": self.password
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"Login failed: {response.status_code} - {response.text}")

    @task(3)
    def get_books(self):
        self.client.get("/api/books?limit=10&offset=0")

    @task(1)
    def check_health(self):
        self.client.get("/api/health")