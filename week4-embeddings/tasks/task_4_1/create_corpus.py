import json

sentences = []
# Cloud Computing cluster
cloud_topics = ["AWS", "Azure", "GCP", "Kubernetes", "Docker", "Serverless", "S3", "EC2", "Lambda", "Terraform"]
cloud_phrases = [
    "is a powerful tool for scaling",
    "provides high availability for applications",
    "helps in automating infrastructure",
    "is essential for modern cloud native apps",
    "reduces the need for manual server management",
    "allows for seamless deployment of containers",
    "offers managed database services",
    "optimizes resource utilization in the cloud",
    "improves the efficiency of CI/CD pipelines",
    "is widely used for storing unstructured data"
]

for topic in cloud_topics:
    for phrase in cloud_phrases:
        sentences.append(f"{topic} {phrase}.")

# Gardening cluster
garden_topics = ["Roses", "Tulips", "Orchids", "Compost", "Mulch", "Pruning", "Fertilizer", "Greenhouse", "Hydroponics", "Soil"]
garden_phrases = [
    "requires careful watering in the summer",
    "blooms beautifully in the spring",
    "needs a nutrient-rich environment to grow",
    "is a key part of organic gardening",
    "helps keep the soil moist",
    "should be done early in the morning",
    "encourages healthy root development",
    "protects plants from harsh winter weather",
    "allows for growing plants without soil",
    "is fundamental for plant health"
]

for topic in garden_topics:
    for phrase in garden_phrases:
        sentences.append(f"{topic} {phrase}.")

with open("corpus.json", "w") as f:
    json.dump(sentences, f, indent=2)

print(f"Created corpus with {len(sentences)} sentences.")
