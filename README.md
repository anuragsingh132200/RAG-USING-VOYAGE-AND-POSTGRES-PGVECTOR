# Retrieval-Augmented Generation (RAG) System

## **Deliverables**

### **1. System Design Overview and Choices Made**
The system is a Retrieval-Augmented Generation (RAG) chatbot designed to ingest, process, and query documents efficiently, leveraging:

- **Architecture**:
  - A **Flask** backend for handling API requests.
  - PostgreSQL as the database for document storage and vector embeddings.
  - SentenceTransformer for generating vector embeddings of document chunks.
  - **Voyage AI** for Large Language Model (LLM) integration to provide contextually accurate responses.

- **why postgres**:
  -Using PostgreSQL with pgvectorscale as your vector database offers several key advantages over dedicated vector databases:

  -PostgreSQL is a robust, open-source database with a rich ecosystem of tools, drivers, and connectors. This ensures transparency, community support, and continuous improvements.

  -By using PostgreSQL, you can manage both your relational and vector data within a single database. This reduces operational complexity, as there's no need to maintain and synchronize multiple databases.

  -Pgvectorscale enhances pgvector with faster search capabilities, higher recall, and efficient time-based filtering. It leverages advanced indexing techniques, such as the DiskANN-inspired index, to significantly speed up Approximate Nearest Neighbor (ANN) searches.

  -Pgvectorscale Vector builds on top of pgvector, offering improved performance and additional features, making PostgreSQL a powerful and versatile choice for AI applications.

- **Design Choices**:
  - **Document Chunking**: Splits documents into manageable 500-character chunks for fine-grained querying.
  - **Embeddings**: Sentence embeddings from SentenceTransformer's `all-MiniLM-L6-v2` model for efficient similarity searches.
  - **PostgreSQL with Vector Storage**: Supports fast similarity searches using PostgreSQL's `pgvector` extension.
  - **Dockerized Deployment**: Ensures reproducibility and ease of scaling.
  - **RESTful API**: Enables ingestion and querying of documents via endpoints.

---

### **2. Local and Deployed Setup Instructions**

#### **Local Setup**

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up PostgreSQL Database**:
   - Install PostgreSQL locally.
   - Create a database and enable the `pgvector` extension:
     ```sql
     CREATE DATABASE rag_db;
     \c rag_db
     CREATE EXTENSION vector;
     ```

5. **Configure Environment Variables**:
   Create a `.env` file with the following:
   ```env
   FLASK_ENV=development
   SQLALCHEMY_DATABASE_URI=postgresql://<username>:<password>@localhost:5432/rag_db
   VOYAGE_API_KEY=<your_voyage_api_key>
   ```

6. **Run the Application**:
   ```bash
   flask run
   ```

#### **Dockerized Setup**

1. **Build the Docker Image**:
   ```bash
   docker build -t rag-system .
   ```

2. **Run the Container**:
   ```bash
   docker run -p 5000:5000 rag-system
   ```

3. **Using Docker Compose**:
   Create a `docker-compose.yml` file (provided in the Dockerfile section above).
   Start the services:
   ```bash
   docker-compose up
   ```

#### **Deployment on Cloud**
You can deploy this system on platforms like AWS, Azure, or GCP. For seamless deployment:
- Use managed database services for PostgreSQL.
- Deploy the Flask app using Docker on services like ECS, AKS, or GKE.

---

### **3. API Documentation with Examples**

#### **Endpoints**

1. **Ingest Document**
   - **Endpoint**: `POST /ingest`
   - **Parameters**:
     - `file`: Document file (PDF, Markdown, or plain text).
     - `type`: File type (`pdf`, `markdown`, or `text`).
     - `title`: Title of the document.
   - **Response**:
     ```json
     {
       "status": "success",
       "message": "Document ingested successfully"
     }
     ```

2. **Query Document**
   - **Endpoint**: `POST /query`
   - **Parameters**:
     - `query`: The user’s query.
   - **Response**:
     ```json
     {
       "results": [
         {
           "chunk": "Relevant chunk of document",
           "source": "Document title"
         }
       ],
       "response": "Final LLM response based on relevant data"
     }
     ```

---

### **4. Cost Analysis (Assuming 1000 Queries/Day)**

| **Component**          | **Estimated Cost**               |
|-------------------------|-----------------------------------|
| **Voyage AI (LLM)**     | $0.01/query × 1000 = $10/day      |
| **PostgreSQL Cloud DB** | ~$30/month (AWS RDS or similar)   |
| **Compute (Flask App)** | ~$50/month (small EC2 instance)   |
| **Storage**             | ~$5/month (for document storage) |

**Total Estimated Monthly Cost**: ~$350/month

---

### **5. Known Limitations and Potential Improvements**

#### **Known Limitations**
1. **Embedding Size**: The embeddings may result in slower query performance for very large datasets.
2. **Limited Context Size**: Chunking limits the scope of relevant data considered.
3. **Scalability**: Single-node deployment may not scale for high query volumes.

#### **Potential Improvements**
1. **Scalable Infrastructure**: Use a distributed architecture (e.g., Kubernetes) for scaling.
2. **Improved Query Efficiency**: Optimize the vector similarity search with tools like FAISS.
3. **Better LLM Integration**: Experiment with advanced LLMs to enhance response quality.
4. **User Authentication**: Add role-based access control for better security.
5. **Cache Results**: Use caching for frequent queries to reduce LLM costs.
