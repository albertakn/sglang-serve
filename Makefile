build:
	docker build -t sglang-serve .

run:
	docker run --rm -it \
		--gpus all \
		--ipc=host \
		--shm-size 32g \
		-p 6666:6666 \
		-p 7860:7860 \
		-v $(HOME)/.cache/huggingface:/root/.cache/huggingface \
		-v $(CURDIR):/workspace \
		sglang-serve /bin/bash
