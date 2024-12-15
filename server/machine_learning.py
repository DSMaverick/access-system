import cv2
import sys
#Import os module for reading training data directories and paths
import os
#Import numpy to convert python lists to numpy arrays as it is needed by OpenCV face recognizers
import numpy as np
import pickle 

#!Using OpenCV-Face-Recogntion-Python! 

#Create our LBPH face recognizer 
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

#Function to detect face using OpenCV
def detect_face(img):
    #Convert the test image to gray image as opencv face detector expects gray images
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #Load OpenCV face detector Haar classifier a more accurate but slow
    face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')

    #Detect multiscale images, result is a list of faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5);
    
    #If no faces are detected then return original img
    if (len(faces) == 0):
        return None, None
    
    #Under the assumption that there will be only one face,
    #Extract the face area
    (x, y, w, h) = faces[0]
    
    #Return only the face part of the image
    return gray[y:y+w, x:x+h], faces[0]

"""This function will read all persons training images, detect face from each image
    and will return two lists of exactly same size, one list 
    of faces and another list of labels for each face"""
def prepare_training_data(data_folder_path):
    
    #--STEP-1--
    #Get the directories (one directory for each subject) in data folder
    dirs = os.listdir(data_folder_path)
    
    #List to hold all subject faces
    faces = []
    #List to hold labels for all subjects
    labels = []
    
    #Go through each directory and read images within it
    for dir_name in dirs:
        
        #Subject directories start with letter 's' so ignore any non-relevant directories if any
        if not dir_name.startswith("s"):
            continue;
            
        #--STEP-2--
        #Extract label number of subject from dir_name
        #Format of dir name = slabel
        label = int(dir_name.replace("s", ""))
        
        #Build path of directory containin images for current subject subject
        #Sample subject_dir_path = "training-data/s1"
        subject_dir_path = data_folder_path + "/" + dir_name
        
        #Get the images names that are inside the given subject directory
        subject_images_names = os.listdir(subject_dir_path)
        
        #--STEP-3--
        #Go through each image name, read image, 
        #detect face and add face to list of faces
        for image_name in subject_images_names:
            
            #Ignore system files like .DS_Store
            if image_name.startswith("."):
                continue;
            
            #Build image path
            #Sample image path = training-data/s1/1.png
            image_path = subject_dir_path + "/" + image_name

            #Read image
            image = cv2.imread(image_path)
            
            #Display an image window to show the image 
            cv2.imshow("Antrenare pe imagine...", cv2.resize(image, (400, 500)))
            cv2.waitKey(100)
            
            #Detect face
            face, rect = detect_face(image)
            
            #--STEP-4--
            #We will ignore faces that are not detected
            if face is not None:
                #Add face to list of faces
                faces.append(face)
                #Add label for this face
                labels.append(label)
            
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    
    return faces, labels

#Function to draw rectangle on image according to given (x, y) coordinates and given width and heigh
def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
#Function to draw text on give image starting from passed (x, y) coordinates. 
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

"""This function recognizes the person in image passed and 
    draws a rectangle around detected face with name of the subject"""
def predict(test_img):
    #Make a copy of the image
    img = test_img.copy()
    #Detect face from the image
    face, rect = detect_face(img)

    #Predict the image using our face recognizer 
    label, confidence = face_recognizer.predict(face)
    #Get name of respective label returned by face recognizer
    print(confidence)
    if confidence < 50:
        label_text = subjects[label]
    else:
        label_text = subjects[0]
        label=0
    
    #Draw a rectangle around face detected
    draw_rectangle(img, rect)
    #Draw name of predicted person
    draw_text(img, label_text, rect[0], rect[1]-5)
    
    return (img,label)

subjects=[]
def run_face_recognition(argvi,argv):
    with open("angajatii.txt","r") as f:
        global subjects
        subjects=f.readlines()
    
    subjects = [str(el.strip()) for el in subjects]
    subjects.insert(0,"unknown")
	
    print("Pregatire Date...")
    if argv == "train":
        faces, labels = prepare_training_data("training-data")
    print("Date pregatite")

#print(faces)
#print(labels)

    print("Salvare in fisier!")

    if argv == "train":
        with open('objs.pkl', 'wb') as f:
            pickle.dump([faces, labels], f)

    print ('Citire din fisier!')
	
    with open('objs.pkl', 'rb') as f:  
        faces_read, labels_read = pickle.load(f)

    faces=faces_read
    labels=labels_read
	
    print("Total faces: ", len(faces))
    print("Total labels: ", len(labels))

    #Train our face recognizer of our training faces
    face_recognizer.train(faces_read, np.array(labels_read))

    print("Predictie a imagini...")

    #Load test images
    test_img1 = cv2.imread(argvi)

    #Perform a prediction
    predicted_img1,i = predict(test_img1)
    print("Predictie completa")

    #Display both images
    #cv2.imshow(subjects[i], cv2.resize(predicted_img1, (400, 500)))
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    #cv2.waitKey(1)
    #cv2.destroyAllWindows()
    return subjects[i]

if __name__ == '__main__':
	print(run_face_recognition(sys.argv[1],sys.argv[2]))
