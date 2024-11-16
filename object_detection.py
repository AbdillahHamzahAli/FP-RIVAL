import numpy as np
import cv2
import time
import json
import os
import signal


FILE_PATH = "./data/posisi_object.json"


class ObjectDetector:
	def __init__(self):
		self.webcam = cv2.VideoCapture(1)

		self.KNOWN_WIDTH = 3.0
		self.P = 100 
		self.D = 20
		self.W = self.KNOWN_WIDTH
		self.FOCAL_LENGTH = (self.P * self.D) / self.W

		self.white_detection_start = {"left": False, "right": False}
		self.blue_detection_start = {"left": False, "right": False}
		self.white_box_visible = False
		self.blue_box_visible = False

		self.kirim_data = False

	def distance_to_camera(self, knownWidth, focalLength, perWidth):
		return (knownWidth * focalLength) / perWidth

	def write_to_json(self, data):
		file_path = FILE_PATH 
		if not os.path.exists(file_path):
			os.makedirs(os.path.dirname(file_path), exist_ok=True)
			with open(file_path, "w") as f:
				json.dump({}, f)

		with open(file_path, "r") as f:
			existing_data = json.load(f)

		if not existing_data:
			existing_data = {"kiri": {"warna": False, "jarak": False}, "kanan": {"warna": False, "jarak": False}}

		for key in ["kiri", "kanan"]:
			if key not in data:
				data[key] = {"warna": False, "jarak": False}

		existing_data.update(data)

		with open(file_path, "w") as f:
			json.dump(existing_data, f)

	def detect_white_objects(self, detection_frame, detection_width, current_time):
		hsvFrame = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2HSV)
		white_lower = np.array([35, 21, 219], np.uint8)
		white_upper = np.array([119, 50, 255], np.uint8)
		white_mask = cv2.inRange(hsvFrame, white_lower, white_upper)
		white_contours, _ = cv2.findContours(white_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		object_data = {"kiri": {"warna": False, "jarak": False}, "kanan": {"warna": False, "jarak": False}}

		for contour in white_contours:
			area = cv2.contourArea(contour)
			if area > 1000:
				x, y, w, h = cv2.boundingRect(contour)
				center_point = (x + w // 2, y + h // 2)
				
				distance = self.distance_to_camera(self.KNOWN_WIDTH, self.FOCAL_LENGTH, w)
				
				if center_point[0] < detection_width // 2:
					if self.white_detection_start["left"] is False:
						self.white_detection_start["left"] = current_time
					if current_time - self.white_detection_start["left"] >= 2:
						object_data["kiri"] = {"warna": "white", "jarak": distance}
						cv2.rectangle(detection_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
						cv2.circle(detection_frame, center_point, 5, (0, 0, 255), -1)
				else:
					if self.white_detection_start["right"] is False:
						self.white_detection_start["right"] = current_time
					if current_time - self.white_detection_start["right"] >= 2:
						object_data["kanan"] = {"warna": "white", "jarak": distance}
						cv2.rectangle(detection_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
						cv2.circle(detection_frame, center_point, 5, (0, 0, 255), -1)

		return object_data, detection_frame

	def detect_blue_objects(self, detection_frame, detection_width, current_time):
		hsvFrame = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2HSV)
		blue_lower = np.array([100, 150, 0], np.uint8)
		blue_upper = np.array([140, 255, 255], np.uint8)
		blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)
		kernel = np.ones((5, 5), "uint8")
		blue_mask = cv2.dilate(blue_mask, kernel)
		blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		object_data = {"kiri": {"warna": False, "jarak": False}, "kanan": {"warna": False, "jarak": False}}

		for contour in blue_contours:
			area = cv2.contourArea(contour)
			if area > 1000:
				x, y, w, h = cv2.boundingRect(contour)
				center_point = (x + w // 2, y + h // 2)
				
				distance = self.distance_to_camera(self.KNOWN_WIDTH, self.FOCAL_LENGTH, w)
				
				if center_point[0] < detection_width // 2:
					if self.blue_detection_start["left"] is False:
						self.blue_detection_start["left"] = current_time
					if current_time - self.blue_detection_start["left"] >= 2:
						object_data["kiri"] = {"warna": "blue", "jarak": distance}
						cv2.rectangle(detection_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
						cv2.circle(detection_frame, center_point, 5, (0, 0, 255), -1)
				else:
					if self.blue_detection_start["right"] is False:
						self.blue_detection_start["right"] = current_time
					if current_time - self.blue_detection_start["right"] >= 2:
						object_data["kanan"] = {"warna": "blue", "jarak": distance}
						cv2.rectangle(detection_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
						cv2.circle(detection_frame, center_point, 5, (0, 0, 255), -1)

		return object_data, detection_frame

	def detect_objects(self):
		while True:
			ret, imageFrame = self.webcam.read()
			height, width = imageFrame.shape[:2]
			
			detection_width = 200
			detection_height = 150
			center_x = (width - detection_width) // 2
			center_y = (height - detection_height) // 2

			cv2.rectangle(imageFrame, (0, center_y), (width, center_y + detection_height), (0, 255, 0), 2)
			cv2.line(imageFrame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)

			detection_frame = imageFrame[center_y:center_y+detection_height, center_x:640]
			current_time = time.time()

			white_data, detection_frame = self.detect_white_objects(detection_frame, detection_width, current_time)
			blue_data, detection_frame = self.detect_blue_objects(detection_frame, detection_width, current_time)

			object_data = {
				"kiri": white_data["kiri"] if white_data["kiri"]["warna"] else blue_data["kiri"],
				"kanan": white_data["kanan"] if white_data["kanan"]["warna"] else blue_data["kanan"]
			}

			self.write_to_json(object_data)

			imageFrame[center_y:center_y+detection_height, center_x:640] = detection_frame

			cv2.imshow("Object Detection", imageFrame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				self.webcam.release()
				cv2.destroyAllWindows()
				break

	def force_quit(self):
		print("Mematikan program secara paksa...")
		self.webcam.release()
		cv2.destroyAllWindows()
		os.kill(os.getpid(), signal.SIGINT)


	def close_on_detection(self):
		while True:
			ret, imageFrame = self.webcam.read()
			height, width = imageFrame.shape[:2]
			
			detection_width = 200
			detection_height = 150
			center_x = (width - detection_width) // 2
			center_y = (height - detection_height) // 2

			cv2.rectangle(imageFrame, (0, center_y), (width, center_y + detection_height), (0, 255, 0), 2)
			cv2.line(imageFrame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)

			detection_frame = imageFrame[center_y:center_y+detection_height, center_x:640]
			current_time = time.time()

			white_data, detection_frame = self.detect_white_objects(detection_frame, detection_width, current_time)
			blue_data, detection_frame = self.detect_blue_objects(detection_frame, detection_width, current_time)

			object_data = {
				"kiri": white_data["kiri"] if white_data["kiri"]["warna"] else blue_data["kiri"],
				"kanan": white_data["kanan"] if white_data["kanan"]["warna"] else blue_data["kanan"]
			}

			self.write_to_json(object_data)

			imageFrame[center_y:center_y+detection_height, center_x:640] = detection_frame

			cv2.imshow("Object Detection", imageFrame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				self.webcam.release()
				cv2.destroyAllWindows()
				break

			if object_data["kiri"]["warna"] or object_data["kanan"]["warna"]:
				print("Objek terdeteksi. Menutup program...")
				self.webcam.release()
				cv2.destroyAllWindows()
				break
			cv2.imshow("Object Detection", imageFrame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				self.webcam.release()
				cv2.destroyAllWindows()
				break


	def detect_for_duration(self, s):
		start_time = time.time()
		while time.time() - start_time < s:
			ret, imageFrame = self.webcam.read()
			height, width = imageFrame.shape[:2]
			
			detection_width = 200
			detection_height = 150
			center_x = (width - detection_width) // 2
			center_y = (height - detection_height) // 2

			cv2.rectangle(imageFrame, (0, center_y), (width, center_y + detection_height), (0, 255, 0), 2)
			cv2.line(imageFrame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)

			detection_frame = imageFrame[center_y:center_y+detection_height, center_x:640]
			current_time = time.time()

			white_data, detection_frame = self.detect_white_objects(detection_frame, detection_width, current_time)
			blue_data, detection_frame = self.detect_blue_objects(detection_frame, detection_width, current_time)

			object_data = {
				"kiri": white_data["kiri"] if white_data["kiri"]["warna"] else blue_data["kiri"],
				"kanan": white_data["kanan"] if white_data["kanan"]["warna"] else blue_data["kanan"]
			}

			self.write_to_json(object_data)

			imageFrame[center_y:center_y+detection_height, center_x:640] = detection_frame

			cv2.imshow("detect_for_duration", imageFrame)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				self.webcam.release()
				cv2.destroyAllWindows()
				break

	def detect_left_object(self):
		ret, imageFrame = self.webcam.read()
		height, width = imageFrame.shape[:2]
		
		detection_width = width // 2
		detection_height = height
		
		cv2.line(imageFrame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)
		
		left_frame = imageFrame[:, :width//2]
		current_time = time.time()
		
		white_data, left_frame = self.detect_white_objects(left_frame, detection_width, current_time)
		blue_data, left_frame = self.detect_blue_objects(left_frame, detection_width, current_time)
		
		object_data = {
			"kiri": white_data["kiri"] if white_data["kiri"]["warna"] else blue_data["kiri"]
		}
		
		self.write_to_json(object_data)
		
		imageFrame[:, :width//2] = left_frame
		
		cv2.imshow("Left Object Detection", imageFrame)
		if cv2.waitKey(10) & 0xFF == ord('q'):
			self.webcam.release()
			cv2.destroyAllWindows()
			return False
		
		return object_data["kiri"]["warna"] is not None



if __name__ == "__main__":
    detector = ObjectDetector()
    detector.detect_left_object()
