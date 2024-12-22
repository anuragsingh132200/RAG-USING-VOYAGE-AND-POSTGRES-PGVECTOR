from flask import Blueprint, request, jsonify
from app.utils import ingest_document,query_documents

main_bp = Blueprint('main', __name__)

@main_bp.route('/ingest', methods=['POST'])
def ingest():
    try:
        file = request.files['file']
        document_type = request.form.get('type', 'text')  # Can be 'pdf', 'markdown', or 'text'
        title = request.form.get('title', 'Untitled')

        # Process the document and save to the database
        response = ingest_document(file, document_type, title)

        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_bp.route('/query', methods=['POST'])
def query():
    query_text = request.form.get('query', '')
    if query_text is None:
        return jsonify({"error": "Query text is required"}), 400

    # Get relevant documents based on query
    relevant_docs = query_documents(query_text)
    print(relevant_docs)
    return jsonify({"results": relevant_docs}), 200
