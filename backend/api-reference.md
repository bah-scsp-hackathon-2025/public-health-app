# Users
```
# Python
requests.post("http://localhost:8000/users/", json={"username": "user-1", "email": "user@email.com", "password": "password"})
requests.get("http://localhost:8000/users/").json()
requests.get("http://localhost:8000/users/1").json()

# Shell
curl http://localhost:8000/users/ -X POST -d '{"username": "user-1", "email": "user@email.com", "password": "password"}' -H "Content-type: application/json"
curl http://localhost:8000/users/
curl http://localhost:8000/users/1
```