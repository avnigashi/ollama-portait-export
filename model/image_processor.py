import os
import cv2
import base64
import requests
from PyQt5.QtCore import QThread, pyqtSignal

class ImageProcessor(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    image_processed = pyqtSignal(str, bool, str, bool, str)  # Updated signal
    processing_finished = pyqtSignal(dict)
    current_image_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.folders = []
        self.output_dir = ""
        self.min_width = 0
        self.min_height = 0
        self.generate_captions = False
        self.caption_limit = None
        self.ai_validation = False
        self.crop_faces = False
        self.allowed_file_types = ['.png', '.jpg', '.jpeg', '.webp']
        self._is_running = False
        self.api_params = {
            'url': 'http://localhost:11434',
            'generate_uri': '/api/generate',
            'model': 'default',
            'prompt': "Return tags describing this picture. Use single words or short phrases separated by commas.",
            'temperature': '0.7',
            'max_tokens': '1000',
            'top_p': '1',
            'frequency_penalty': '0',
            'presence_penalty': '0'
        }
        self.model = None

    def set_parameters(self, folders, output_dir, min_width, min_height, generate_captions,
                       caption_limit, ai_validation, crop_faces):
        self.folders = folders
        self.output_dir = output_dir
        self.min_width = min_width
        self.min_height = min_height
        self.generate_captions = generate_captions
        self.caption_limit = caption_limit
        self.ai_validation = ai_validation
        self.crop_faces = crop_faces

    def set_api_params(self, api_params):
        self.api_params.update(api_params)

    def set_model(self, model):
        self.model = model

    def is_running(self):
        return self._is_running

    def stop(self):
        self._is_running = False

    def run(self):
        self._is_running = True
        total_files = sum(len([f for f in os.listdir(folder) if f.lower().endswith(tuple(self.allowed_file_types))]) for folder in self.folders)
        processed_files = 0
        stats = {
            'total_images': total_files,
            'faces_found': 0,
            'no_faces': 0,
            'small_images': 0,
            'failed_validation': 0,
            'processed_successfully': 0
        }

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        for folder in self.folders:
            if not self._is_running:
                break
            for image_file in os.listdir(folder):
                if not self._is_running:
                    break
                if image_file.lower().endswith(tuple(self.allowed_file_types)):
                    image_path = os.path.join(folder, image_file)
                    self.current_image_update.emit(image_path)
                    self.status_update.emit(f"Processing {image_file}...")

                    image = cv2.imread(image_path)

                    height, width = image.shape[:2]
                    if width < self.min_width or height < self.min_height:
                        stats['small_images'] += 1
                        self.image_processed.emit(image_file, False, "Small image", False, "")
                    else:
                        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                        if len(faces) > 0:
                            stats['faces_found'] += 1
                            (x, y, w, h) = faces[0]
                            if self.crop_faces:
                                cropped_face = image[y:y+h, x:x+w]
                                was_cropped = True
                            else:
                                cropped_face = image
                                was_cropped = False

                            process_image = True
                            ai_response = ""
                            if self.ai_validation:
                                process_image, ai_response = self.validate_image(cropped_face)
                                if not process_image:
                                    stats['failed_validation'] += 1
                                    self.image_processed.emit(image_file, False, "Failed AI validation", was_cropped, ai_response)
                                    continue

                            if process_image:
                                cropped_path = os.path.join(self.output_dir, image_file)
                                cv2.imwrite(cropped_path, cropped_face)

                                if self.generate_captions:
                                    ai_response = self.generate_caption(cropped_path)

                                stats['processed_successfully'] += 1
                                self.image_processed.emit(image_file, True, "Processed successfully", was_cropped, ai_response)
                        else:
                            stats['no_faces'] += 1
                            self.image_processed.emit(image_file, False, "No face detected", False, "")

                    processed_files += 1
                    self.progress_update.emit(int((processed_files / total_files) * 100))

        self.processing_finished.emit(stats)
        self._is_running = False

    def validate_image(self, image):
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        response = self.make_ai_request(image_base64, "Validate if this image contains a human face. Respond with only 'yes' or 'no' but then explain.")
        return response.lower() == 'yes', response

    def generate_caption(self, image_path):
        with open(image_path, "rb") as file:
            image_base64 = base64.b64encode(file.read()).decode('utf-8')

        caption = self.make_ai_request(image_base64, self.api_params['prompt'])

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        caption_dir = os.path.join(self.output_dir, "captions")
        os.makedirs(caption_dir, exist_ok=True)
        caption_path = os.path.join(caption_dir, f"{base_name}.txt")
        with open(caption_path, "w") as caption_file:
            caption_file.write(caption)

        return caption

    def make_ai_request(self, image_base64, prompt):
        url = f"{self.api_params['url']}{self.api_params['generate_uri']}"

        payload = {
            "model": self.model or self.api_params['model'],
            "prompt": prompt,
            "images": [image_base64],
            "options": {
                "temperature": float(self.api_params['temperature']),
                "max_tokens": int(self.api_params['max_tokens']),
                "top_p": float(self.api_params['top_p']),
                "frequency_penalty": float(self.api_params['frequency_penalty']),
                "presence_penalty": float(self.api_params['presence_penalty'])
            },
            "stream": False
        }

        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get('response', 'No response generated')
        else:
            print(f"Error in AI request: {response.status_code} - {response.text}")
            return f"Error: {response.status_code} - {response.text}"