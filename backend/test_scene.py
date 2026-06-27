import asyncio

from agent.decision_engine import DecisionEngine
from perception.afferens_client import AfferensClient
from perception.scene_builder import SceneBuilder


async def main():

    client = AfferensClient()

    perception = await client.get_vision()
    print("Perception Response:")
    print(perception)
    print()

    print("\nDetected Objects:")

    if perception.get("status") == 200 and perception.get("data"):

        objects = perception["data"][0]["data"].get("objects", [])

        for obj in objects:
            print(f"{obj['label']} ({obj['confidence']:.2f})")

    else:

        print("\nNo live perception available.")

    scene = SceneBuilder.build(perception)

    decision = DecisionEngine.analyze(scene)

    print("\nDecision:")
    print(decision)

    print(scene)

    print(scene.objects)


asyncio.run(main()) 