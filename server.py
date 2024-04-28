from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import numpy as np
import cv2
from image_process import ML
from chatgpt import chatgpt
import os

SAVE_DIR = "./data/uploaded_images" # 画像保存ディレクトリ
if not os.path.isdir(SAVE_DIR):
    os.mkdir(SAVE_DIR)

app = Flask(__name__, static_url_path="")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images/<path:path>')
def send_js(path):
    return send_from_directory(SAVE_DIR, path)

@app.route('/clear')
def clear():
    return redirect('/')

@app.route('/upload', methods=['POST'])
def upload():
    if request.files['image']:
        # 画像保存ディレクトリ内の画像を削除
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            os.unlink(file_path)

        # 入力画像をモデルが処理可能な形式に変換
        stream = request.files['image'].stream
        img_array = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, 1) # Shape = (高さ, 幅, チャンネル数) dtype = uint8
        # 処理された画像を保存
        fixed_filename = "uploaded_image.png"
        save_path = os.path.join(SAVE_DIR, fixed_filename)
        cv2.imwrite(save_path, img)
        # 入力画像から食材を検出
        # food_names = ML(img)
        # print(f"food_names: {food_names}")
        food_names = ["卵", "鶏肉", "七味"]

        #  フォームで選択されたテキストを取得
        selected_item = request.form['item']  
        print("選択されたアイテム:", selected_item)

        prompt = f"{'、'.join(food_names)}と{selected_item}を使った3つのレシピの料理名と材料と手順を挙げてください。このとき、{selected_item}は必ず使用してください。また、材料の分量を必ず教えてください\
        出力のフォーマット：\
            ・料理名1\
                材料\
                手順\
            ・料理名2\
                材料\
                手順\
            ・料理名3\
                材料\
                手順\
            "

        # # 食材名のリストからプロンプトを生成
        # prompt = f"{'、'.join(food_names)}を使った3つのレシピの料理名と材料と手順を挙げてください。材料の分量を必ず教えてください\
        # 出力のフォーマット：\
        #     ・料理名1\
        #         材料\
        #         手順\
        #     ・料理名2\
        #         材料\
        #         手順\
        #     ・料理名3\
        #         材料\
        #         手順\
        #     "

        # プロンプトからレシピを提案
        recipes = chatgpt(prompt)
        names = [recipe['name'] for recipe in recipes]
        ingredients = [recipe['ingredients'].replace(" ", "&nbsp;").replace('\n', '<br>') for recipe in recipes]
        procedures = [recipe['procedure'].replace(" ", "&nbsp;").replace('\n', '<br>') for recipe in recipes]

        images = os.listdir(SAVE_DIR)[::-1]

        return render_template('index.html', images=images, names=names, ingredients=ingredients, procedures=procedures)
    
    return redirect('/')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8888)