import requests
import json

class LivAI:
    hindi_translit_rev = []
    url = 'https://devlong.liv.ai/translate_api/translate/transliterate/'

    payload = {}

    headers = {
        "Authorization": "Token 8bac6f72ac07e51d2f4af6a7f8256c44a1d5aa12",
        "Content-Type": "application/json"
    }

    def generate_payload(self, text, action_flag):
        self.payload["input_text"] = text
        self.payload["action_flag"] = action_flag

    def call(self, field):
        try:
            r = requests.post(self.url, data=json.dumps(self.payload), headers=self.headers)
            obj = json.loads(r.content)
            return obj['detail'][field]
        except:
            print(r.content)
            return []


if __name__ == '__main__':
    client = LivAI()
    # world level classification
    client.generate_payload("seller bhai takat nahi", "FOR_WC")
    a = client.call()
    print(a)
    # rev transliteration (hi -> en)
    # client.generate_payload("seller bhai takat nahi", "REV")
