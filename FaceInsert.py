import zipfile
import os
from PIL import Image
import io

class ImageExtractor:
    def __init__(self, zip_path, extract_to):
        self.zip_path = zip_path
        self.extract_to = extract_to

    def ExtractImages(self):
        if not os.path.exists(self.extract_to):
            os.makedirs(self.extract_to)

        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.extract_to)
    
    def GetImages(self):
        images = []
        for root, dirs, files in os.walk(self.extract_to):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_path = os.path.join(root, file)
                    with open(image_path, 'rb') as img_file:
                        img = Image.open(io.BytesIO(img_file.read()))
                        images.append(img)
        
        return images

zip_path = './sample_data/Gitanjali.zip'
extract_to = './'
extractor = ImageExtractor(zip_path, extract_to)
images = extractor.ExtractImages()



