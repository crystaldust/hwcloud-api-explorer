from services import ListImages
import json

images_info = ListImages.call(__imagetype='private')
# images_info = ListImages.call(image_type='private', visibility='private')
print(json.dumps(images_info, indent=2))

for img in images_info[0]['images']:
    print(img['name'], img['id'])

print(len(images_info))