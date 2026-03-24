from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/review', methods=['POST'])
def review():
    text = request.form.get('document_text', '').strip()
    if not text:
        result = 'No text provided.'
    else:
        length = len(text)
        words = len(text.split())
        result = (
            f'Review summary:\n- Length: {length} chars\n- Words: {words} words\n'
            f'- Detected high-level risk areas: Injection, Misconfiguration, Data Leakage (simulated)\n'
            '\n(This is a placeholder result from the Flask portal.)'
        )

    return render_template('index.html', result=result)

@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
