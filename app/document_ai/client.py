from google.cloud import documentai_v1 as documentai
from google.cloud.documentai_v1 import Document
from typing import Optional, Dict, Any
import os

class DocumentAIClient:
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "logistics-5u-ai")
        self.location = os.getenv("DOCUMENT_AI_LOCATION", "eu") # Revert to EU based on console
        self.processor_id = os.getenv("DOCUMENT_AI_PROCESSOR_ID", "5710554318b4699b") # For classification
        self.client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": f"{self.location}-documentai.googleapis.com"})
        self.name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    def classify_document(self, file_content: bytes, mime_type: str) -> Dict[str, Any]:
        """
        Classify a document using Document AI
        """
        try:
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.name, # Using the default classification processor
                raw_document=documentai.RawDocument(
                    content=file_content,
                    mime_type=mime_type
                )
            )

            # Process the document
            result = self.client.process_document(request=request)
            document = result.document

            # Debugging: Print all entities and their confidences
            print("Document AI raw entities:")
            if document.entities:
                print(f"Total number of entities found: {len(document.entities)}")
                for i, entity in enumerate(document.entities):
                    # Use getattr for robustness in printing debug info
                    entity_type = getattr(entity, 'type_', 'N/A')
                    entity_confidence = getattr(entity, 'confidence', 'N/A')
                    entity_mention_text = getattr(entity, 'mention_text', 'N/A')
                    print(f"  Entity {i}: type={entity_type}, confidence={entity_confidence}, mention_text={entity_mention_text}")
                    # Print additional entity information if available
                    if hasattr(entity, 'normalized_value'):
                        print(f"    normalized_value: {entity.normalized_value}")
                    if hasattr(entity, 'properties'):
                        print(f"    properties: {entity.properties}")
            else:
                print("  No entities found.")

            # Extract classification results
            document_type = "unknown"
            classification_confidence = 0.0
            classification_metadata = []
            highest_confidence_entity = None

            if document.entities:
                for entity in document.entities:
                    # Convert entity properties to a list of dictionaries
                    properties_list = []
                    if hasattr(entity, 'properties'):
                        for prop in entity.properties:
                            properties_list.append({
                                'name': getattr(prop, 'name', None),
                                'value': getattr(prop, 'value', None)
                            })

                    classification_metadata.append({
                        "type": entity.type_,
                        "mention_text": getattr(entity, 'mention_text', None),
                        "confidence": getattr(entity, 'confidence', None),
                        "normalized_value": str(getattr(entity, 'normalized_value', None)) if getattr(entity, 'normalized_value', None) is not None else None,
                        "properties": properties_list
                    })

                    if highest_confidence_entity is None or \
                       (hasattr(entity, 'confidence') and entity.confidence is not None and \
                        entity.confidence > highest_confidence_entity.confidence):
                        highest_confidence_entity = entity

                if highest_confidence_entity:
                    document_type = highest_confidence_entity.mention_text if highest_confidence_entity.mention_text else highest_confidence_entity.type_
                    classification_confidence = highest_confidence_entity.confidence

            classification = {
                "confidence": classification_confidence,
                "type": document_type,
                "text": document.text if document.text else "",
                "mime_type": document.mime_type,
                "page_count": len(document.pages) if document.pages else 0,
                "classification_metadata": classification_metadata
            }

            return classification

        except Exception as e:
            print(f"Error classifying document: {str(e)}")
            return {
                "error": str(e),
                "confidence": 0.0,
                "type": "error",
                "text": "",
                "mime_type": mime_type,
                "page_count": 0
            } 
            
    def extract_document_entities(self, file_content: bytes, mime_type: str, processor_id: str) -> Dict[str, Any]:
        """
        Extracts entities from a document using a specified Document AI processor.
        """
        try:
            # Create a new client and processor path for the extraction processor
            extraction_client = documentai.DocumentProcessorServiceClient(client_options={"api_endpoint": f"{self.location}-documentai.googleapis.com"})
            extraction_processor_name = extraction_client.processor_path(
                self.project_id, self.location, processor_id
            )

            request = documentai.ProcessRequest(
                name=extraction_processor_name,
                raw_document=documentai.RawDocument(
                    content=file_content,
                    mime_type=mime_type
                )
            )

            result = extraction_client.process_document(request=request)
            document = result.document

            extracted_data = {}
            if document.entities:
                for entity in document.entities:
                    entity_type = entity.type_
                    # Prioritize normalized_value if available, otherwise mention_text
                    if entity.normalized_value and hasattr(entity.normalized_value, 'text'):
                        extracted_data[entity_type] = entity.normalized_value.text
                    elif entity.mention_text:
                        extracted_data[entity_type] = entity.mention_text
                    elif hasattr(entity, 'text_anchor') and entity.text_anchor.content:
                        # Fallback to content from text_anchor if present
                        extracted_data[entity_type] = entity.text_anchor.content
                    else:
                        extracted_data[entity_type] = None # Or handle as per your requirement

            print(f"✅ Document extraction result (Processor {processor_id}): {extracted_data}")
            return {"extracted_data": extracted_data}

        except Exception as e:
            print(f"❌ Error extracting document entities (Processor {processor_id}): {str(e)}")
            return {"error": str(e)} 