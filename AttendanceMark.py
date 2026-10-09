import json
import os

import mysql.connector
from deepface import DeepFace


def get_db_config():
    missing = [
        name for name in ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and configure the values."
        )

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }


class DatabaseEmebeddingsInsert:
    def __init__(self):
        config = get_db_config()
        self.connection = mysql.connector.connect(**config)
        self.cursor = None
        self.face_folder_path = "./sample_data"
        self.embeddings_file_path = "./embeddings.json"

    def OpenEmbeddings(self):
        """
        To open the json embeddings file and return it
        """
        with open(self.embeddings_file_path, "r") as f:
            embeddings = json.load(f)
        return embeddings

    def InsertEmbeddings(self):
        """
        Insert the embeddings into the database
        """
        lst_face_embeddings = []
        models = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace", "GhostFaceNet"]
        first_name = input("Enter the first name")
        last_name = input("Enter the last name")
        middle_name = input("Enter the middle name")
        email = input("Enter the email")
        contact = input("Enter the contact")
        position = input("Enter the position")
        gender = input("Enter your gender")

        embeddings_data = self.OpenEmbeddings()
        self.cursor = self.connection.cursor(buffered=True)
        query = "select * from employee"
        results = self.cursor.execute(query)
        NumOfRows = self.cursor.rowcount
        NumOfRows = NumOfRows + 1

        flag = 0

        for folder in os.listdir(self.face_folder_path):
            print(folder)
            if folder == first_name:
                print("\n name is found")
                image_path = os.path.join(self.face_folder_path, folder, "image1.jpg")
                flag = 1
                try:
                    with open(image_path, "rb") as file:
                        binary_data = file.read()
                except Exception as e:
                    image_path = image_path.replace(".jpg", ".png")
                    print(image_path)
                    with open(image_path, "rb") as file:
                        binary_data = file.read()
                    print(f"Error in reading the image : {e}")
                if os.path.isdir(os.path.join("./sample_data", folder)):
                    for image in os.listdir(os.path.join("./sample_data", folder)):
                        if image.endswith(".jpg") or image.endswith(".jpeg") or image.endswith(".png"):
                            embeddings = DeepFace.represent(os.path.join("./sample_data", folder, image), model_name=models[6], detector_backend="retinaface", align=True)
                            lst_face_embeddings.append(embeddings[0]["embedding"])
                print("\n embeddings are created")
                embeddings_data[folder] = {"embeddings": lst_face_embeddings, "id": NumOfRows}
                json_embeddings = json.dumps({"embeddings": lst_face_embeddings})
                query = """
                    INSERT INTO employee (
                        id, name, middle_name, surname, contact, email_id, position, gender, face_embedding, photo
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    NumOfRows, first_name, middle_name, last_name, contact, email,
                    position, gender, json_embeddings, binary_data
                )
                try:
                    self.cursor.execute(query, values)
                    self.connection.commit()
                    with open("./embeddings.json", "w") as file:
                        json.dump(embeddings_data, file, indent=4)
                    print("\n query has been executed")
                except Exception as e:
                    print(f"Error in query execution: {e}")

        if flag == 0:
            print("Either your data in avaiable at the defined repository or you have enter the wrong or misspelled name , please rectify that")

        self.cursor.close()


db = DatabaseEmebeddingsInsert()
db.InsertEmbeddings()
