# Function Execution Flow Charts

## 1. Document Upload Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Processor
    participant Storage
    
    User->>Frontend: Select File
    Frontend->>Frontend: Validate Size (1GB)
    
    alt File Valid
        Frontend->>API: POST /api/documents
        API->>Processor: Process Document
        
        par Document Processing
            Processor->>Processor: Extract Content
            Processor->>Processor: Generate Metadata
        and Vector Generation
            Processor->>Storage: Generate Embeddings
            Storage->>Storage: Store Vectors
        end
        
        Storage-->>API: Storage Confirmation
        API-->>Frontend: Success Response
        Frontend-->>User: Show Results
    else File Invalid
        Frontend-->>User: Show Error
    end
    
    note over Frontend,API: Hardware Requirements:<br/>RAM: 16GB<br/>CPU: 4GHz<br/>No GPU
```

## 2. Code Analysis Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Analyzer
    participant VectorDB
    participant LLM
    
    User->>Frontend: Enter Code
    Frontend->>Frontend: Validate Input
    
    alt Input Valid
        Frontend->>API: POST /api/analyze
        
        par Vector Search
            API->>VectorDB: Find Similar Code
            VectorDB-->>Analyzer: Similar Examples
        and LLM Analysis
            API->>LLM: Generate Analysis
            LLM-->>Analyzer: Analysis Results
        end
        
        Analyzer->>Analyzer: Combine Results
        Analyzer-->>API: Complete Analysis
        API-->>Frontend: Analysis Response
        Frontend-->>User: Display Results
    else Input Invalid
        Frontend-->>User: Show Error
    end
    
    note over Frontend,API: Performance Target:<br/>Analysis Time < 3s
```

## 3. Code Generation Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant VectorDB
    participant Generator
    participant LLM
    
    User->>Frontend: Enter Description
    Frontend->>Frontend: Validate Input
    
    alt Input Valid
        Frontend->>API: POST /api/generate
        
        par Context Gathering
            API->>VectorDB: Find Similar Code
            VectorDB-->>Generator: Context Examples
        and Prompt Creation
            Generator->>Generator: Create Prompt
        end
        
        Generator->>LLM: Generate Code
        LLM-->>Generator: Generated Code
        Generator->>Generator: Format Output
        Generator-->>API: Final Code
        API-->>Frontend: Code Response
        Frontend-->>User: Display Code
    else Input Invalid
        Frontend-->>User: Show Error
    end
    
    note over Frontend,API: Performance Target:<br/>Generation Time < 10s
```

## 4. Training System Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Trainer
    participant Processor
    participant VectorDB
    
    User->>Frontend: Enter Directory
    Frontend->>Frontend: Validate Path
    
    alt Path Valid
        Frontend->>API: POST /api/train
        API->>Trainer: Initialize Training
        
        loop For Each File
            Trainer->>Processor: Process File
            Processor->>Processor: Extract Content
            Processor->>Processor: Generate Chunks
            
            par Vector Generation
                Processor->>VectorDB: Generate Vectors
                VectorDB->>VectorDB: Store Vectors
            and Metadata Processing
                Processor->>Processor: Extract Metadata
                Processor->>VectorDB: Store Metadata
            end
            
            VectorDB-->>Trainer: Confirm Storage
        end
        
        Trainer-->>API: Training Complete
        API-->>Frontend: Success Status
        Frontend-->>User: Show Results
    else Path Invalid
        Frontend-->>User: Show Error
    end
    
    note over Frontend,API: Hardware Usage:<br/>RAM: Up to 16GB<br/>CPU: 4GHz Load
```

## 5. Component Interaction Flow
```mermaid
graph TD
    A[Frontend Components] -->|API Calls| B[Backend API]
    B -->|Responses| A
    
    subgraph "Frontend Layer"
        A -->|State Updates| C[React Components]
        C -->|User Input| D[Event Handlers]
        D -->|API Requests| A
    end
    
    subgraph "API Layer"
        B -->|Routes| E[API Controllers]
        E -->|Processing| F[Core Services]
    end
    
    subgraph "Processing Layer"
        F -->|Document Processing| G[Document Processor]
        F -->|Vector Operations| H[Vector Database]
        F -->|Code Generation| I[LLM Interface]
    end
    
    subgraph "Storage Layer"
        G -->|Store| J[File Storage]
        H -->|Index| K[Vector Storage]
        I -->|Cache| L[Response Cache]
    end
    
    note over "Frontend Layer","Storage Layer": System Requirements:<br/>RAM: 16GB<br/>CPU: 4GHz<br/>Storage: Based on usage
```

## 6. Error Handling Flow
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Services
    
    User->>Frontend: Action
    
    alt Frontend Validation
        Frontend->>Frontend: Validate Input
        Frontend-->>User: Show Error
    else API Error
        Frontend->>API: Request
        API->>API: Validate Request
        API-->>Frontend: Error Response
        Frontend-->>User: Show Error
    else Service Error
        Frontend->>API: Request
        API->>Services: Process
        Services-->>API: Error
        API-->>Frontend: Error Response
        Frontend-->>User: Show Error
    end
    
    note over Frontend,API: Error Categories:<br/>Validation Errors<br/>Processing Errors<br/>System Errors
```

## 7. State Management Flow
```mermaid
graph TD
    A[User Action] -->|Trigger| B[Event Handler]
    B -->|Update| C[Local State]
    B -->|API Call| D[Backend API]
    D -->|Response| C
    C -->|Render| E[UI Update]
    
    subgraph "State Types"
        F[File State]
        G[Code State]
        H[Result State]
        I[Error State]
    end
    
    C -->|Manages| F
    C -->|Manages| G
    C -->|Manages| H
    C -->|Manages| I
    
    note over "State Types": Memory Usage:<br/>Efficient state management<br/>within 16GB RAM limit
```

## 8. Performance Flow
```mermaid
graph LR
    A[Request] -->|Process| B[API Layer]
    B -->|Handle| C[Processing Layer]
    
    subgraph "Performance Targets"
        D[Upload: <5s]
        E[Analysis: <3s]
        F[Generation: <10s]
    end
    
    C -->|Meet| D
    C -->|Meet| E
    C -->|Meet| F
    
    note over "Performance Targets": Hardware Specs:<br/>4GHz CPU<br/>16GB RAM<br/>No GPU acceleration
```
