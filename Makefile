# Build Docker Images
build-backend:
	docker build -t my-mlops-backend:latest -f app/backend/Dockerfile app/backend

build-frontend:
	docker build -t my-mlops-frontend:latest -f app/frontend/Dockerfile app/frontend

# Train the ML Model
train:
	docker run --rm -v $(PWD)/data:/app/data -v $(PWD)/models:/app/models my-mlops-backend:latest python train.py
	

# DVC Tracking
dvc-track:
	dvc add models/
	git add models.dvc .gitignore
	git commit -m "Track model directory with DVC"

dvc-push:
	dvc push

dvc-pull:
	dvc pull

# Kubernetes Deployment
deploy:
	kubectl apply -f k8s/

clean:
	kubectl delete -f k8s/ || true
