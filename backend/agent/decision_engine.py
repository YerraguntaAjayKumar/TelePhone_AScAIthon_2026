class DecisionEngine:

    @staticmethod
    def analyze(scene):

        if scene.person:

            if scene.phone:
                return {
                    "state": "DISTRACTED",
                    "message": "Phone detected. Stay focused!"
                }

            elif scene.book:
                return {
                    "state": "STUDYING",
                    "message": "Study session in progress."
                }

            else:
                return {
                    "state": "PRESENT",
                    "message": "User is at the desk."
                }

        return {
            "state": "ABSENT",
            "message": "User has left the workspace."
        }