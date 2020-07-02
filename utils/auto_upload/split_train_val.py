import json


validation_percent = 0.1

with open("datasets/train_master_mini.json", "r") as json_file:
    master = json.load(json_file)


train = {k: v for k,v in master.items()}
train["annotations"] = master["annotations"][0:int((1.0-validation_percent)*len(master["annotations"]))]
highest_image_id = train["annotations"][-1]["image_id"]
images = []
for image in master["images"]:
    if image["id"] <= highest_image_id:
        images.append(image)
train["images"] = images
with open("datasets/train_split.json", "w") as json_file:
    json.dump(train, json_file)


test = {k : v for k,v in master.items()}
test["annotations"] = master["annotations"][int((1.0-validation_percent)*len(master["annotations"])):]
lowest_image_id = test["annotations"][0]["image_id"]
images = []
for image in master["images"]:
    if image["id"] >= lowest_image_id:
        images.append(image)
test["images"] = images
with open("datasets/val_split.json", "w") as json_file:
    json.dump(test, json_file)