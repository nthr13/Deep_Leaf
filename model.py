# from inference_sdk import InferenceHTTPClient

# CLIENT = InferenceHTTPClient(
#     api_url="https://serverless.roboflow.com",
#     api_key="ITyKMhMBi3HKoKsM5PrY"
# )

# try:
#     result = CLIENT.infer("image_1.jpg", model_id="detecting-diseases/5")
#     # print(result)
#     predictions = result['predictions']
#     # print(predictions)
    
#     for prediction in predictions:
#         # print(f"prediction: {prediction}")
#         print(f"Disease: {prediction['class']} Confidence: {prediction['confidence']}")
# except Exception as e:
#     print(f"An error occurred: {e}")


import base64
from inference_sdk import InferenceHTTPClient

# 1. Setup Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="ITyKMhMBi3HKoKsM5PrY"
)

# 2. Read your image and convert it to base64 string
with open("./image/image_1.jpg", "rb") as image_file:
    image_bytes = image_file.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")  # ✅ Ensure UTF-8 string

# 3. Infer with base64 (no "data:image/jpeg;base64," prefix)
result = CLIENT.infer(image_b64, model_id="detecting-diseases/5")

print(result)
