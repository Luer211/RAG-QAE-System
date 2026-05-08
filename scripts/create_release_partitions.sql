-- Replace :release_id and :partition_suffix in your migration runner.
-- Partition suffix should be sanitized, for example rel_20260508_001.

CREATE TABLE documents_:partition_suffix
PARTITION OF documents
FOR VALUES IN (':release_id');

CREATE TABLE chunks_:partition_suffix
PARTITION OF chunks
FOR VALUES IN (':release_id');

CREATE TABLE chunk_embeddings_:partition_suffix
PARTITION OF chunk_embeddings
FOR VALUES IN (':release_id');

