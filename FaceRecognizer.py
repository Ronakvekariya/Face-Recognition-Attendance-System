    from deepface import DeepFace
    import numpy as np
    from scipy.spatial.distance import cosine
    import json
    import cv2
    import time

    class Recongnizer:

        def __init__(self):
            self.results = []
            self.models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace",  "GhostFaceNet"]
            self.embeddings_file_path = "./embeddings.json"
            self.embeddings = None

        def OpenEmbeddings(self):
            """
            To open the json embeddings file and return it
            """
            with open(self.embeddings_file_path , "r") as f:
                embeddings = json.load(f)
            return embeddings
        
        def FaceRecongnition(self , image , threshold = 0.5):
            """
            Recognize multiple faces in an image and match them with stored embeddings.

            Parameters:
                image (str): Path to the input image.
                embeddings (dict): Dictionary of stored embeddings.
                models (list): List of model names (ensure the required model is in the list).
                threshold (float): Threshold for cosine similarity to classify a face as recognized.

            Returns:
                results (list): List of recognized names or "Unknown" for each face in the image.
            """
            start_time = time.time()
            self.embeddings = self.OpenEmbeddings()

            try:
                # Detect faces
                faces = DeepFace.extract_faces(img_path=image, detector_backend='opencv')
                detection_duration = time.time() - start_time
                print(f"\nDetected {len(faces)} face(s) in {detection_duration:.2f} seconds.\n")

                # If no faces are detected
                if not faces:
                    return ["No face detected"]

                for face_data in faces:
                    try:
                        # Extract the cropped face image
                        face_image = face_data['face']
                        facial_area = face_data['facial_area']

                        
                        # Generate embeddings for the detected face
                        embedding_start_time = time.time()
                        test_embeddings = DeepFace.represent(
                            img_path=face_image, 
                            model_name=self.models[6], 
                            detector_backend="skip", 
                            align=True
                        )
                        embedding_duration = time.time() - embedding_start_time
                        print(f"\nEmbedding generated in {embedding_duration:.2f} seconds.\n")

                        # Compare with stored embeddings
                        min_distance = float('inf')
                        recognized_name = "Unknown"

                        for key1 in self.embeddings:

                            for key2 in self.embeddings[key1]:
                                for index in range(len(self.embeddings[key1]["embeddings"])):
                                    stored_embedding = self.embeddings[key1]["embeddings"][index]
                                    distance = cosine(test_embeddings[0]["embedding"], stored_embedding)
                                    if distance < min_distance:
                                        min_distance = distance
                                        recognized_name = key1 if distance <= threshold else "Unknown"
                        
                        # Append the result for the current face
                        self.results.append((recognized_name, min_distance , facial_area , self.embeddings[recognized_name]["id"]))
                
                    except Exception as e:
                        print(f"Error processing a face: {str(e)}")
                        self.results.append("Error processing face")

                total_duration = time.time() - start_time
                print(f"\nProcessed all faces in {total_duration:.2f} seconds.\n")

            except Exception as e:
                print(f"An error occurred: {str(e)}")
                return ["Error in face detection or recognition"]

            return self.results
        
        def InAction(self):
            faces = None
            # Initialize the webcam (0 is usually the default camera)
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                print("Error: Could not open the webcam.")
                exit()

            print("Press 'C' to capture an image or 'Q' to quit.")

            while True:
                # Capture frame-by-frame
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: Could not read frame from webcam.")
                    break

                # Display the resulting frame
                cv2.imshow('Webcam', frame)

                # Wait for a key press
                key = cv2.waitKey(1) & 0xFF

                if key == ord('c'):
                    filename = f'./test.jpg'
                    cv2.imwrite(filename, frame)
                    print(f"Image captured and saved as '{filename}'.")
                    faces = self.FaceRecongnition(filename)
                    print(faces)
                    

                    for result_data in faces:             
                        if type(result_data) != str:
                            x , y , w ,h = result_data[2]['x'] ,  result_data[2]['y'] ,  result_data[2]['w'] ,  result_data[2]['y']
                            cv2.rectangle(frame , (x,y) , (x+w , y+h) , (123,255,0) , 2)
                            cv2.putText(frame , f"{result_data[0]}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 12, 0), 1)
                        else:
                            print("There was no face in the image to detect")
                    
                        cv2.imshow("faces with recongnized faces" , frame)
                    
                    break

                elif key == ord('q'):
                    print("Exiting...")
                    break

            # Release the webcam and close all OpenCV windows
            cap.release()
            cv2.destroyAllWindows()
            return faces

    if __name__ == "__main__":
        system = Recongnizer()
        system.InAction()



            



