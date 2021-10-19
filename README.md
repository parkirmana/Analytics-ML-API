# Analytics-ML-API
A collection of machine learning model API for Smart Parking Analytics Website

## How to Run
1. Run `pip install -r requirements.txt`
2. Run `python preparation.py`
3. Download pre-trained yolov4 [here](https://drive.google.com/drive/folders/14td_wB0K0g0AAKLKAMMj872_dXeKCWl0?usp=sharing).</br>
You'll find `config`, `label` and `weight` file there. Download the three file and put them in directory `saved_models/yolov4/`.
5. Download pre-trained efficienynet_d1 [here](https://drive.google.com/drive/folders/1u8jmqmsku0QCZcQnzKSYFP0WU3U4jvtr?usp=sharing).</br>
You'll find `config` and `checkpoint` file. Download both of them and put them in directory `saved_models/tfod/workspace/models/efficientnet_d1_coco17`.
7. Download `label` file for efficientnet_d1 model [here](https://drive.google.com/drive/folders/1tbKOLc2srxj8PLlkUhVtzCOMyctH-E-7?usp=sharing).
Download `label.pbtxt` file and put it inside directory `saved_models/tfod/workspace/annotations/`.
9. Please update the database configuration in `core/db_config.py`.
10. Please update the `host` and `port` to run the apllication in `app.py`.
11. Last, run `python app.py` to run application.
