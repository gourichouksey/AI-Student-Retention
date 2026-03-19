import requests
import json

with open('backend/training/dataset.csv', 'rb') as f:
    r = requests.post(
        'http://127.0.0.1:5000/batch/predict',
        files={'file': f}
    )
    print('Status code:', r.status_code)
    print('Response:')
    print(json.dumps(r.json(), indent=2))