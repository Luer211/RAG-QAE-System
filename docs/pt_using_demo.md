# 分区表的使用demo

给出一个使用概念demo，与项目正式表名不同。
涉及如何建表、建立索引、插入数据、查询数据...

## 设计假设

假设我们有：
- knowledge_base_versions  知识库版本表
- documents                文档表

每次上传一批文档时，这批文档都属于某一个 kb_version_id。
就比如说：
- 版本 v1: kb_version_id = 101
- 版本 v2: kb_version_id = 102
- 版本 v3: kb_version_id = 103
那么我们的文档表可以按 kb_version_id 分区：
- documents_v101
- documents_v102
- documents_v103

PGSQL的官方文档里，支持多种声明式分区，我们这里使用 LIST 分区。

## 建立数据表

1. 建立知识库版本表
```sql
CREATE TABLE knowledge_base_versions (
    kb_version_id BIGINT PRIMARY KEY,
    knowledge_base_id BIGINT NOT NULL,
    version_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

2. 建立分区父表 documents
```sql
CREATE TABLE documents (
    kb_version_id BIGINT NOT NULL,
    document_id BIGSERIAL NOT NULL,

    title TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_url TEXT,
    content TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- 主键要求包含分区键
    PRIMARY KEY (kb_version_id, document_id)
) PARTITION BY LIST (kb_version_id);
```

## 使用

1. 插入几个知识库版本
```sql
INSERT INTO knowledge_base_versions (
    kb_version_id,
    knowledge_base_id,
    version_name
) VALUES
    (101, 1, 'v1'),
    (102, 1, 'v2'),
    (201, 2, 'v1');
```

2. 给每个知识库版本创建 documents 分区

比如对版本101：
```sql
CREATE TABLE documents_v101
PARTITION OF documents
FOR VALUES IN (101);
```

比如对版本102：
```sql
CREATE TABLE documents_v102
PARTITION OF documents
FOR VALUES IN (102);
```

比如对版本201：
```sql
CREATE TABLE documents_v201
PARTITION OF documents
FOR VALUES IN (201);
```

这里的：
- documents_v101
- documents_v102
- documents_v201
就是具体的分区名。

3. 插入文档

平时插入数据时，也就是插入文档时，不用插入具体的分区表，而是插入父表 documents：
```sql
INSERT INTO documents (
    kb_version_id,
    title,
    file_name,
    file_url,
    content,
    metadata
) VALUES
    (
        101,
        '产品介绍',
        'product_intro.pdf',
        'https://example.com/product_intro.pdf',
        '这里是文档正文内容...',
        '{"type": "pdf", "pages": 12}'::jsonb
    ),
    (
        101,
        '使用手册',
        'manual.docx',
        'https://example.com/manual.docx',
        '这里是使用手册内容...',
        '{"type": "docx"}'::jsonb
    );
```
PostgreSQL 会自动把 kb_version_id = 101 的数据放到 documents_v101 分区里去的。

4. 查询某个版本的文档

我们在业务代码里需要查看某个知识库版本的文档的时候，还是查父表：
```sql
SELECT document_id, title, file_name, uploaded_at
FROM documents
WHERE kb_version_id = 101
ORDER BY uploaded_at DESC;
```
因为 WHERE kb_version_id = 101 命中了分区键，PostgreSQL 就只扫描 documents_v101，不用扫其他版本分区了。

5. 给分区表创建索引

我们这里就可以直接对父表建索引的。
因为在 PostgreSQL 的声明式分区里，对父表创建索引，到实际执行层面就是变成为对一个个分区创建对应的分区索引结构。
所以类似于我们对标题创建索引的话，就直接：
```sql
CREATE INDEX idx_documents_title
ON documents (title);
```