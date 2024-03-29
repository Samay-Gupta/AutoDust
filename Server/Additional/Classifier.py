import numpy as np
import cv2
import os

class ObjectDetection:
    def __init__(self, folder='', confidence=50):
        self.dir = folder
        self.confidence = float(confidence)/100
        self.threshold = 0.3
        print(self.dir, os.getcwd())
        self.LABELS = open(self.dir+"coco.names"if self.dir!='' else "coco.names").read().strip().split("\n")
        np.random.seed(42)
        self.COLORS = np.random.randint(0, 255, size=(len(self.LABELS), 3),dtype="uint8")
        weightsPath = self.dir+"/yolov3.weights"if self.dir!='' else "yolov3.weights"
        configPath = self.dir+"/yolov3.cfg"if self.dir!='' else "yolov3.cfg"
        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

    def load(self, img='img.jpg'):
        image = cv2.imread(img)
        return image

    def show(self, image_data, name='Image'): 
        cv2.imshow(name, image_data)
        cv2.waitKey(0)
        
    def save(self, image_data, file='clf.jpg'):
        cv2.imwrite(file, image_data)

    def categorise(self, detections):
        if len(detections) == 0:
            return 0
        biodegradable = ["bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "potted plant"]
        if detections[0][0] in biodegradable:
            return 1
        else:
            return 0

    def classify(self, img_data):
        image = img_data
        (H, W) = image.shape[:2]
        ln = self.net.getLayerNames()
        ln = [ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layerOutputs = self.net.forward(ln)
        boxes = []
        confidences = []
        classIDs = []
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > self.confidence:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence, self.threshold)
        data = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                color = [int(c) for c in self.COLORS[classIDs[i]]]
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                text = "{}: {:.4f}".format(self.LABELS[classIDs[i]], confidences[i])
                cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 10, color, 5)
                data.append((self.LABELS[classIDs[i]], confidences[i]))
        res = {"image_data":image, 
               "detections":sorted(data, key = lambda classification: classification[1], reverse=True)} 
        return res
