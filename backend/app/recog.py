import face_recognition
from PIL import Image, ImageDraw
import numpy as np
import pymysql
from PIL import Image
from io import BytesIO
import base64

isLoaded = False
known_face_encodings = []
known_face_names = []
known_face_ids = []

def dbcon():
    db = pymysql.connect(
            host="localhost",
            port=3307,
            db="test",
            user="root", 
            password="1qazxc"
    )
    return db


def enroll(img_list, name_list, id_list):
    # This is an example of running face recognition on a single image
    # and drawing a box around each person that was identified.

    for img, name, id in zip(img_list, name_list, id_list):
        # Load a sample picture and learn how to recognize it.
        
        # image = face_recognition.load_image_file(img)
        
        image = Image.frombytes('RGB', (640, 480), img, 'raw')
        image = np.asarray(image)
        # print(image)
        # face_encoding = face_recognition.face_encodings(image)
        # print(len(image))

        # print(len(face_recognition.face_encodings(image)))
        
        # print(name)

        face_encoding = face_recognition.face_encodings(image)[0]
        
        # Create arrays of known face encodings and their names
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
        known_face_ids.append(id)

def recognition(img):
    # Load an image with an unknown face
    # unknown_image = face_recognition.load_image_file(img)
    unknown_image = Image.frombytes('RGB', (640, 480), img, 'raw')
    unknown_image = np.asarray(unknown_image)
    # Find all the faces and face encodings in the unknown image
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(unknown_image)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    name_list =[]
    id_list = []
    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:

            name = known_face_names[best_match_index]
            name_list.append(name)

            id = known_face_ids[best_match_index]
            id_list.append(id)
            
            print(id, name)
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # Display the resulting image
    pil_image.show()

    # print(name) 
    return name_list, id_list

def realtime_recognition(img, location):
    # Load an image with an unknown face
    # unknown_image = face_recognition.load_image_file(img)
    unknown_image = Image.frombytes('RGB', (640, 480), img, 'raw')
    unknown_image = np.asarray(unknown_image)
    # Find all the faces and face encodings in the unknown image
    face_locations = face_recognition.face_locations(unknown_image)
    face_encodings = face_recognition.face_encodings(unknown_image, face_locations)

    # Convert the image to a PIL-format image so that we can draw on top of it with the Pillow library
    # See http://pillow.readthedocs.io/ for more about PIL/Pillow
    pil_image = Image.fromarray(unknown_image)
    # Create a Pillow ImageDraw Draw instance to draw with
    draw = ImageDraw.Draw(pil_image)

    name_list =[]
    id_list = []
    # Loop through each face found in the unknown image
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            name_list.append(name)

            id = known_face_ids[best_match_index]
            id_list.append(id)

            print(id, name)
        # Draw a box around the face using the Pillow module
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Draw a label with a name below the face
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Remove the drawing library from memory as per the Pillow docs
    del draw

    # insert logs
    for id in id_list:
        set_log_to_db(id, location)



    # for name in name_list:
    #     set_log_to_db(user_id)

    # Display the resulting image
    # pil_image.show()

    # print(name) 
    return name_list, id_list

def set_log_to_db(user_id, location ="Main Entrance", activity = "None"):
    db = dbcon()
    cursor = db.cursor()
    SQL = '''
        INSERT INTO visit_log (id, user_id, location, activity, date)
        VALUES (NULL, %s, %s, %s, now())
    '''
    cursor.execute(SQL, (user_id, location, activity))
    db.commit()

def get_img_from_db(id):
    db = pymysql.connect(
            host="localhost",
            port=3307,
            db="test",
            user="root", 
            password="1qazxc"
        )

    cursor = db.cursor()
    SQL = 'SELECT face_image FROM target  where user_id = {id};'
    cursor.execute(SQL.format(id= id))

    aaa = cursor.fetchall()
    # print(aaa)
    img = aaa[0][0]
    # print(img)

    image = Image.frombytes('RGB', (640, 480), img, 'raw')
    # image.show()
    return img

def get_img_from_db2():
    db = pymysql.connect(
            host="localhost",
            port=3307,
            db="test",
            user="root", 
            password="1qazxc"
        )

    cursor = db.cursor()
    SQL = 'SELECT face_image, name, user_id FROM test.user2;'
    cursor.execute(SQL)

    aaa = cursor.fetchall()
    
    imgs =[]
    names =[]
    ids = []
    for data in aaa:
        imgs.append(data[0])
        names.append(data[1])
        ids.append(data[2])

    return imgs, names, ids


if __name__ == '__main__':

    pass

    # imgs, names = get_img_from_db2()
    # enroll(imgs, names)

    # img = get_img_from_db(4)
    # recognition(img)

       