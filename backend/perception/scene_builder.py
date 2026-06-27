from models.scene import Scene


class SceneBuilder:

    @staticmethod
    def build(perception):

        scene = Scene()

        if perception["status"] != 200:
            return scene

        events = perception.get("data", [])

        if not events:
            return scene

        objects = events[0]["data"].get("objects", [])

        for obj in objects:

         confidence = obj["confidence"]

          # Ignore weak detections
         if confidence < 0.60:
          continue

         label = obj["label"].lower()

         scene.objects.append(label)

         if label == "person":
             scene.person = True

         elif label == "cell phone":
            scene.phone = True

         elif label == "book":
            scene.book = True

         elif label == "cup":
            scene.cup = True

         elif label == "bottle":
            scene.bottle = True

         elif label == "backpack":
            scene.backpack = True

         elif label == "laptop":
            scene.laptop = True

         elif label == "keyboard":
            scene.keyboard = True

         elif label == "mouse":
            scene.mouse = True

        return scene