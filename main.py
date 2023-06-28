from flask import Flask, render_template, request, redirect
import os
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df

def get_file_info():
    files_info = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(file_path):
            df = pd.read_csv(file_path)
            columns = df.columns.tolist()
            files_info.append({'filename': filename, 'columns': columns})
    return files_info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            return redirect('/')
    return render_template('index.html')

@app.route('/files')
def files():
    files_info = get_file_info()
    return render_template('files.html', files_info=files_info)

@app.route('/delete_file/<filename>')
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect('/files')

@app.route('/file/<filename>')
def file_data(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = load_csv(file_path)
    columns = df.columns.tolist()

    filter_columns = request.args.getlist('filter_column')
    filter_values = request.args.getlist('filter_value')

    filtered_df = df
    if filter_columns and filter_values:
        for column, value in zip(filter_columns, filter_values):
            filtered_df = filtered_df[filtered_df[column] == value]

    sort_columns = request.args.getlist('sort_column')
    if sort_columns:
        filtered_df = filtered_df.sort_values(sort_columns)
    
    data = filtered_df.to_dict(orient='records')
    return render_template('file_data.html', filename=filename, columns=columns, data=data)

if __name__ == '__main__':
    app.run(debug=True)