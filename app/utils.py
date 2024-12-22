import pdfplumber
import markdown
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer
from app.config import Config
from scipy.spatial.distance import cosine
from voyageai import VoyageClient   # Import Voyage AI Client

# Initialize the Voyage AI client (with your API key)
client = VoyageClient(api_key=Config.VOYAGE_AI_API_KEY)
# Initialize Sentence-Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # Pre-trained model to generate embeddings

# Function to extract text from PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to extract text from Markdown file
def extract_text_from_markdown(file):
    md = file.read().decode('utf-8')
    return markdown.markdown(md)

# Function to extract text from a plain text file
def extract_text_from_text(file):
    return file.read().decode('utf-8')

# Function to process uploaded documents based on file type
def process_document(file, document_type):
    if document_type == 'pdf':
        return extract_text_from_pdf(file)
    elif document_type == 'markdown':
        return extract_text_from_markdown(file)
    elif document_type == 'text':
        return extract_text_from_text(file)
    return ""

# Function to split text into smaller chunks
def chunk_text(text, chunk_size=500):
    """
    Splits text into smaller chunks of the given size.
    """
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# Function to generate embeddings for text using Sentence-Transformer
def generate_embedding(text):
    return model.encode(text).tolist()  # Converts numpy array to list for PostgreSQL compatibility

# Function to save document chunks and their embeddings to PostgreSQL
def save_chunk_to_db(title, chunk_id, chunk_content, embedding):
    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO document_chunks (document_title, chunk_id, chunk_content, embedding)
        VALUES (%s, %s, %s, %s)
    """, (title, chunk_id, chunk_content, embedding))
    conn.commit()
    cur.close()
    conn.close()

# Main function to handle document ingestion
def ingest_document(file, document_type, title):
    # Step 1: Process the document to extract text
    content = process_document(file, document_type)

    # Step 2: Chunk the text into smaller parts
    chunks = chunk_text(content)

    # Step 3: For each chunk, generate embeddings and save to the database
    for idx, chunk in enumerate(chunks):
        embedding = generate_embedding(chunk)  # Generate embedding for each chunk
        save_chunk_to_db(title, idx, chunk, embedding)  # Save each chunk with its embedding and identifier

    return {"status": "success", "message": "Document ingested successfully"}

# Function to retrieve relevant documents based on a query
def query_documents(query_text, top_k=5):
    """
    Retrieve the most relevant chunks from the database based on the query text.

    Args:
        query_text (str): The text of the query.
        top_k (int): The number of top relevant chunks to return.

    Returns:
        list: A list of dictionaries containing relevant chunks and their metadata.
    """
    # Generate embedding for the query text
    query_embedding = generate_embedding(query_text)

    conn = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()

    # Fetch all chunks and their embeddings
    cur.execute("""
        SELECT document_title, chunk_id, chunk_content, embedding
        FROM document_chunks
    """)
    results = cur.fetchall()
    cur.close()
    conn.close()

    # Calculate cosine similarity for each chunk
    relevant_chunks = []
    for row in results:
        title, chunk_id, content, embedding = row
        embedding = np.array(embedding)  # Convert PostgreSQL array back to numpy array
        similarity = 1 - cosine(query_embedding, embedding)  # Compute cosine similarity
        relevant_chunks.append({
            "title": title,
            "chunk_id": chunk_id,
            "content": content,
            "similarity": similarity
        })

    # Sort chunks by similarity in descending order and return the top_k results
    relevant_chunks = sorted(relevant_chunks, key=lambda x: x['similarity'], reverse=True)
    return relevant_chunks[:top_k]

# Function to generate a response using Voyage AI's LLM
def generate_llm_response(query_text, relevant_docs):
    try:
        # Format the context for the LLM
        context = "\n\n".join([f"Title: {doc['title']}\nContent: {doc['content']}" for doc in relevant_docs])

        # Prepare the prompt with the query and the relevant documents
        prompt = f"Query: {query_text}\n\nContext:\n{context}\n\nAnswer:"

        # Send the prompt to Voyage AI's LLM for generating a response
        response = client.complete(prompt)

        return response['text'].strip()  # Return the response text from LLM

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return "Sorry, I couldn't generate an answer at the moment."
