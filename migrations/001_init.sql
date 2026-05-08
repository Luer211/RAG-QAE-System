CREATE EXTENSION IF NOT EXISTS vector;

CREATE TYPE release_status AS ENUM (
    'draft',
    'testing',
    'ready',
    'published',
    'archived'
);

CREATE TYPE evaluation_run_status AS ENUM (
    'pending',
    'running',
    'partial_success',
    'success',
    'failed'
);

CREATE TABLE knowledge_releases (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status release_status NOT NULL DEFAULT 'draft',
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_knowledge_releases_name UNIQUE (name)
);

CREATE TABLE documents (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    title VARCHAR(512) NOT NULL,
    content_raw TEXT NOT NULL,
    content_cleaned TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_documents PRIMARY KEY (release_id, id),
    CONSTRAINT fk_documents_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE
) PARTITION BY LIST (release_id);

CREATE TABLE chunks (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    document_id UUID NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('simple', content)
    ) STORED,
    char_count INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_chunks PRIMARY KEY (release_id, id),
    CONSTRAINT fk_chunks_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_chunks_document
        FOREIGN KEY (release_id, document_id)
        REFERENCES documents(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_chunks_release_document_chunk_index
        UNIQUE (release_id, document_id, chunk_index)
) PARTITION BY LIST (release_id);

CREATE INDEX idx_chunks_search_vector
ON chunks
USING GIN (search_vector);

CREATE TABLE chunk_embeddings (
    id UUID NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    embedding_model VARCHAR(255) NOT NULL,
    embedding_dim INTEGER NOT NULL,
    vector VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_chunk_embeddings PRIMARY KEY (release_id, id),
    CONSTRAINT fk_chunk_embeddings_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_chunk_embeddings_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_chunk_embeddings_release_chunk_model
        UNIQUE (release_id, chunk_id, embedding_model)
) PARTITION BY LIST (release_id);

CREATE INDEX idx_chunk_embeddings_vector_hnsw_cosine
ON chunk_embeddings
USING hnsw (vector vector_cosine_ops);

CREATE TABLE retrieval_logs (
    id VARCHAR(64) PRIMARY KEY,
    release_id VARCHAR(64) NOT NULL,
    query_raw TEXT NOT NULL,
    query_rewritten TEXT NULL,
    rewrite_used VARCHAR(255) NULL,
    answer_text TEXT NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_retrieval_logs_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_retrieval_logs_id_release
        UNIQUE (id, release_id)
);

CREATE TABLE retrieval_items (
    id VARCHAR(64) PRIMARY KEY,
    retrieval_log_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    source_type VARCHAR(64) NOT NULL,
    raw_score DOUBLE PRECISION NOT NULL,
    rerank_score DOUBLE PRECISION NULL,
    rank_before_rerank INTEGER NULL,
    rank_after_rerank INTEGER NULL,
    selected_for_context BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_retrieval_items_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_retrieval_items_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE
);

CREATE TABLE answer_citations (
    id VARCHAR(64) PRIMARY KEY,
    retrieval_log_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    chunk_id UUID NOT NULL,
    citation_order INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_answer_citations_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_answer_citations_chunk
        FOREIGN KEY (release_id, chunk_id)
        REFERENCES chunks(release_id, id)
        ON DELETE CASCADE,
    CONSTRAINT uq_answer_citations_log_order
        UNIQUE (retrieval_log_id, citation_order),
    CONSTRAINT uq_answer_citations_log_chunk
        UNIQUE (retrieval_log_id, chunk_id)
);

CREATE TABLE evaluation_datasets (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_evaluation_datasets_name UNIQUE (name)
);

CREATE TABLE evaluation_questions (
    id VARCHAR(64) PRIMARY KEY,
    dataset_id VARCHAR(64) NOT NULL,
    question_text TEXT NOT NULL,
    reference_answer TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluation_questions_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES evaluation_datasets(id)
        ON DELETE CASCADE
);

CREATE TABLE evaluation_runs (
    id VARCHAR(64) PRIMARY KEY,
    release_id VARCHAR(64) NOT NULL,
    dataset_id VARCHAR(64) NOT NULL,
    config_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    run_status evaluation_run_status NOT NULL DEFAULT 'pending',
    total_count INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluation_runs_release
        FOREIGN KEY (release_id)
        REFERENCES knowledge_releases(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_runs_dataset
        FOREIGN KEY (dataset_id)
        REFERENCES evaluation_datasets(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_evaluation_runs_id_release
        UNIQUE (id, release_id)
);

CREATE TABLE evaluation_items (
    id VARCHAR(64) PRIMARY KEY,
    evaluation_run_id VARCHAR(64) NOT NULL,
    question_id VARCHAR(64) NOT NULL,
    release_id VARCHAR(64) NOT NULL,
    retrieval_log_id VARCHAR(64) NULL,
    answer_text TEXT NULL,
    citations_snapshot JSONB NOT NULL DEFAULT '[]'::jsonb,
    judge_result JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluation_items_run
        FOREIGN KEY (evaluation_run_id, release_id)
        REFERENCES evaluation_runs(id, release_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_items_question
        FOREIGN KEY (question_id)
        REFERENCES evaluation_questions(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_evaluation_items_retrieval_log
        FOREIGN KEY (retrieval_log_id, release_id)
        REFERENCES retrieval_logs(id, release_id)
        ON DELETE CASCADE
);

CREATE TABLE evaluation_metrics (
    id VARCHAR(64) PRIMARY KEY,
    evaluation_run_id VARCHAR(64) NOT NULL,
    metric_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_evaluation_metrics_run
        FOREIGN KEY (evaluation_run_id)
        REFERENCES evaluation_runs(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_evaluation_metrics_run_id
        UNIQUE (evaluation_run_id)
);

