# src/qa_module.py

import groq
import chromadb
from typing import Dict, Any
from Promts import prompt as prompt_dict 




import groq
import chromadb
from typing import Dict, Any
from Promts import prompt as prompt_dict, role as role_dict

import groq
import chromadb
from typing import Dict, Any
from Promts import prompt as prompt_dict, role as role_dict

def get_ai_response(query_type, question, client, collection):
    # Retrieve relevant information from the Chroma database
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    # Construct the prompt based on the query type and retrieved information
    prompts = {
        "Tallman": prompt_dict.get(1, "Default Tallman prompt"),
        "Sales": prompt_dict.get(2, "Default Sales prompt"),
        "Product": prompt_dict.get(3, "Default Product prompt"),
        "Tutorial": prompt_dict.get(4, "Default Tutorial prompt")
    }

    selected_prompt = prompts.get(query_type, "Default general prompt")

    context = "\n".join(results['documents'][0])
    prompt = f"{selected_prompt}\nUse the following context to answer the question: {context}\n\nQuestion: {question}\nAnswer:"

    # Generate the AI response
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": role_dict.get(1, "Default system role")},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",  # Use an appropriate model
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred while generating the response: {str(e)}"

# ... rest of the file remains the same ...

# ... rest of the file remains the same ...
def save_correction(answer: str, improvement: str, collection: chromadb.Collection):
    # Combine the original answer and the improvement
    corrected_answer = f"Original: {answer}\nImprovement: {improvement}"

    # Add the corrected answer to the Chroma database
    collection.add(
        documents=[corrected_answer],
        metadatas=[{"type": "correction"}],
        ids=[f"correction_{len(collection.get()['ids']) + 1}"]
    )

def reload_database(chroma_client, collection, qa_data_path):
    # Delete the entire collection
    chroma_client.delete_collection(collection.name)
    
    # Recreate the collection
    collection = chroma_client.create_collection("tallman_knowledge")
    
    # Load new data from the qa_data_path (assuming it's a file containing the new knowledge)
    with open(qa_data_path, 'r') as qa_file:
        qa_data = qa_file.readlines()  # Adjust based on your file structure (JSON, CSV, etc.)
    
    # Insert the new data back into the collection
    for line in qa_data:
        # Process each line of the QA data and add it to the collection
        question, answer = line.split('|')  # Example splitting data, adjust this to your format
        collection.add(
            documents=[answer],
            metadatas=[{"question": question}],
            ids=[question]
        )
