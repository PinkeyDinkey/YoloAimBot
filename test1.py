import numpy as np
import cv2
from PIL import ImageGrab as ig
import time
with open('obj.names', 'r') as f:
    classes = f.read().splitlines()

net = cv2.dnn.readNetFromDarknet('yolov4-obj.cfg', 'yolov4.weights')

model = cv2.dnn_DetectionModel(net)
model.setInputParams(scale=1 / 255, size=(416, 416), swapRB=True)
last_time = time.time()
while(True):
    screen = ig.grab(bbox=(50,50,800,640))
    img = np.array(screen)
    #try:
    classIds, scores, boxes = model.detect(np.array(screen), confThreshold=0.6, nmsThreshold=0.4)
    for (classId, score, box) in zip(classIds, scores, boxes):
        cv2.rectangle(np.array(screen), (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
                      color=(0, 255, 0), thickness=2)

        text = '%s: %.2f' % (classes[classId[0]], score)
        cv2.putText(np.array(screen), text, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    color=(0, 255, 0), thickness=2)
    #except:
       #pass
    print('Loop took {} seconds',format(time.time()-last_time))
    cv2.imshow("test", img)
    last_time = time.time()
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break